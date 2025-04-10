using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;
using System.Linq;

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

    private async Task<ChatResponse> SendAsync(ChatRequest chatRequest, bool verbose = false)
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
                return chatResponse;
            }
            else
            {
                if (verbose)
                    Debug.LogError("Error: " + request.error + " | " + request.downloadHandler.text);

                return null;
            }
        }
    }

    public async Task<string> StartConversationAsync(string systemMessage, string userMessage, string model, bool enableFunctionCalling, bool verbose = false)
    {
        List<ChatMessage> conversationHistory = new List<ChatMessage>
        {
            new ChatMessage { role = "system", content = systemMessage },
            new ChatMessage { role = "user", content = userMessage }
        };

        ChatRequest initialRequest = new ChatRequest
        {
            model = model,
            messages = conversationHistory,
            Functions = enableFunctionCalling ? functionDefinitions.ToList() : null,
        };

        ChatResponse chatResponse = await SendAsync(initialRequest, verbose);
        if (chatResponse != null && chatResponse.choices != null && chatResponse.choices.Count > 0)
        {
            ChatMessage responseMessage = chatResponse.choices[0].message;
            conversationHistory.Add(responseMessage);

            if (responseMessage.FunctionCall != null && enableFunctionCalling)
            {
                return await CallFunctionAsync(conversationHistory, responseMessage, model, verbose);
            }
            else
            {
                if (verbose)
                    Debug.Log("Assistant response: " + responseMessage.content);

                return responseMessage.content;
            }
        }
        else
        {
            return "Assistant didn't respond in StartConversationAsync.";
        }
    }

    private async Task<string> ContinueConversationWithFunctionResultAsync(List<ChatMessage> conversationHistory, string model, bool verbose = false)
    {
        ChatRequest newRequest = new ChatRequest
        {
            model = model,
            messages = conversationHistory,
            Functions = functionDefinitions.ToList(),
        };

        ChatResponse chatResponse = await SendAsync(newRequest, verbose);
        if (chatResponse?.choices != null && chatResponse.choices.Count > 0)
        {
            ChatMessage responseMessage = chatResponse.choices[0].message;
            conversationHistory.Add(responseMessage);

            if (responseMessage.FunctionCall != null)
            {
                return await CallFunctionAsync(conversationHistory, responseMessage, model, verbose);
            }
            else
            {
                if (verbose)
                    Debug.Log("Assistant response: " + responseMessage.content);

                return responseMessage.content;
            }
        }

        return "Assistant didn't respond in ContinueConversationWithFunctionResultAsync.";
    }

    private async Task<string> CallFunctionAsync(List<ChatMessage> conversationHistory, ChatMessage message, string model, bool verbose = false)
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

            return await ContinueConversationWithFunctionResultAsync(conversationHistory, model, verbose);
        }
        else
        {
            if (verbose)
                Debug.Log("LLM called \"" + message.FunctionCall.name + "\" with keys {" + string.Join(" ", args.Keys) + "} and values {" + string.Join(" ", args.Values) + "} but it does not exist.");

            return "The function " + message.FunctionCall.name + " does not exist.";
        }
    }
}
