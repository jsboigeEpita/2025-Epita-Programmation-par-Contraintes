using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;
using System.Linq;
using static ApiInteraction;

public class ApiInteraction : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private ApiKeys apiKeys;

    private static Dictionary<string, Func<Dictionary<string, string>, Task<string>>> functionMapping = new Dictionary<string, Func<Dictionary<string, string>, Task<string>>>
    {

    };

    private static List<FunctionDefinition> functionDefinitions = new List<FunctionDefinition>
    {

    };

    #region JSON Objects
    [System.Serializable]
    public class FunctionCall
    {
        [JsonProperty("name")]
        public string name { get; set; }

        [JsonProperty("arguments")]
        public string arguments { get; set; }
    }

    [System.Serializable]
    public class FunctionDefinition
    {
        [JsonProperty("name")]
        public string name { get; set; }

        [JsonProperty("description")]
        public string description { get; set; }

        [JsonProperty("parameters")]
        public string parameter { get; set; }
    }

    [System.Serializable]
    public class ChatMessage
    {
        [JsonProperty("role")]
        public string role { get; set; } // user, function

        [JsonProperty("content")]
        public string content { get; set; }

        [JsonProperty("function_call", NullValueHandling = NullValueHandling.Ignore)]
        public FunctionCall FunctionCall { get; set; }
    }

    [System.Serializable]
    public class ChatRequest
    {
        [JsonProperty("model")]
        public string model { get; set; }

        [JsonProperty("messages")]
        public List<ChatMessage> messages { get; set; }

        [JsonProperty("functions", NullValueHandling = NullValueHandling.Ignore)]
        public List<FunctionDefinition> Functions { get; set; }
    }

    [System.Serializable]
    public class ChatChoice
    {
        [JsonProperty("message")]
        public ChatMessage message { get; set; }
    }

    [System.Serializable]
    public class ChatResponse
    {
        [JsonProperty("choices")]
        public List<ChatChoice> choices { get; set; }
    }
    #endregion

    private async IAsyncEnumerable<ChatResponse> Send(ChatRequest chatRequest, bool verbose = false)
    {
        string jsonContent = JsonConvert.SerializeObject(chatRequest);

        using (UnityWebRequest request = new UnityWebRequest(apiKeys.endpoint, "POST"))
        {
            byte[] jsonBytes = Encoding.UTF8.GetBytes(jsonContent);
            request.uploadHandler = new UploadHandlerRaw(jsonBytes);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {apiKeys.key}");

            if (verbose)
                Debug.Log("Sending request: " + jsonContent);

            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string responseText = request.downloadHandler.text;
                if (verbose)
                    Debug.Log("Received response: " + responseText);

                var chatResponse = JsonConvert.DeserializeObject<ChatResponse>(responseText);
                yield return chatResponse;
            }
            else
            {
                if (verbose)
                    Debug.LogError("Error: " + request.error);

                yield return null;
            }
        }
    }

    public async IAsyncEnumerable<string> StartConversation(string message, string model, bool enableFunctionCalling, bool verbose = false)
    {
        List<ChatMessage> conversationHistory = new List<ChatMessage>();

        ChatMessage userMessage = new ChatMessage { role = "user", content = message };
        conversationHistory.Add(userMessage);

        ChatRequest initialRequest = new ChatRequest
        {
            model = model,
            messages = conversationHistory,
            Functions = enableFunctionCalling ? functionDefinitions.ToList() : new List<FunctionDefinition>(),
        };

        await foreach (ChatResponse chatResponse in Send(initialRequest, verbose))
        {
            if (chatResponse?.choices != null && chatResponse.choices.Count > 0)
            {
                ChatMessage responseMessage = chatResponse.choices[0].message;
                conversationHistory.Add(responseMessage);

                if (responseMessage.FunctionCall != null && enableFunctionCalling)
                {
                    await foreach (string result in CallFunction(conversationHistory, responseMessage, model, verbose))
                    {
                        yield return result;
                    }
                }
                else
                {
                    if (verbose)
                        Debug.Log("Assistant response: " + responseMessage.content);

                    yield return responseMessage.content;
                }
            }
            else
            {
                yield return "Assistant didn't respond.";
            }
        }
    }

    private async IAsyncEnumerable<string> ContinueConversationWithFunctionResult(List<ChatMessage> conversationHistory, string model, bool verbose = false)
    {
        ChatRequest newRequest = new ChatRequest
        {
            model = model,
            messages = conversationHistory,
            Functions = functionDefinitions.ToList(),
        };

        await foreach (var chatResponse in Send(newRequest, true))
        {
            if (chatResponse?.choices != null && chatResponse.choices.Count > 0)
            {
                ChatMessage responseMessage = chatResponse.choices[0].message;
                conversationHistory.Add(responseMessage);

                if (responseMessage.FunctionCall != null)
                {
                    await foreach (string result in CallFunction(conversationHistory, responseMessage, model, verbose))
                    {
                        yield return result;
                    }
                }
                else
                {
                    if (verbose)
                        Debug.Log("Assistant response: " + responseMessage.content);

                    yield return responseMessage.content;
                }
            }
        }
    }

    private async IAsyncEnumerable<string> CallFunction(List<ChatMessage> conversationHistory, ChatMessage message, string model, bool verbose = false)
    {
        Dictionary<string, string> args = JsonConvert.DeserializeObject<Dictionary<string, string>>(message.FunctionCall.arguments);

        if (functionMapping.ContainsKey(message.FunctionCall.name))
        {
            if (verbose)
                Debug.Log("LLM called \"" + message.FunctionCall.name + "\" with keys {" + string.Join(" ", args.Keys) + "} and values {" + string.Join(" ", args.Values) + "}.");

            string result = await functionMapping[message.FunctionCall.name](args);

            if (verbose)
                Debug.Log("Got result: " + result);

            ChatMessage functionResultMessage = new ChatMessage
            {
                role = "function",
                content = result
            };

            conversationHistory.Add(functionResultMessage);

            await foreach (string continuousResult in ContinueConversationWithFunctionResult(conversationHistory, model, verbose))
            {
                yield return continuousResult;
            }
        }
        else
        {
            if (verbose)
                Debug.Log("LLM called \"" + message.FunctionCall.name + "\" with keys {" + string.Join(" ", args.Keys) + "} and values {" + string.Join(" ", args.Values) + "} but it does not exist.");

            yield return "The function " + message.FunctionCall.name + " does not exist.";
        }
    }
}
