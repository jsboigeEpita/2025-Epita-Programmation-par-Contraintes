using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;
using System.Linq;
using System.Collections;
using UnityEngine.Events;
using static ApiInteraction;

public class ApiInteraction : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private ApiKeys apiKeys;
    
    public static string function1(int a, string b)
    {
        System.Threading.Thread.Sleep(1000);
        return $"Function 1 called with a: {a}, b: {b}";
    }

    public static string function1Dico(Dictionary<string, string> args)
    {
        int a = int.Parse(args["a"]);
        string b = args["b"];
        return function1(a, b);
    }

    private static Dictionary<string, Func<Dictionary<string, string>, string>> functionMapping = new Dictionary<string, Func<Dictionary<string, string>, string>>
    {
        { "function1", function1Dico }
    };

    private static List<FunctionDefinition> functionDefinitions = new List<FunctionDefinition>
    {
        new FunctionDefinition(
            "function1",
            "This is the first function",
            new FunctionParameters(
                "object", 
                new { 
                    a = new ArgProperties() {
                        type = "integer",
                        description = "the desc of the first arg"
                    },
                    b = new ArgProperties() {
                        type = "string",
                        description = "the desc of the second arg"
                    } 
                }, 
                new string[] {"a", "b"},
                false
            )
        )
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
    public class FunctionParameters
    {
        [JsonProperty("type")]
        public string type { get; set; }

        [JsonProperty("properties")]
        public object properties { get; set; }

        [JsonProperty("required")]
        public string [] required { get; set; }

        [JsonProperty("additionalProperties")]
        public bool additionalProperties { get; set; }

        public FunctionParameters(string type, object properties, string[] required, bool additionalProperties)
        {
            this.type = type;
            this.properties = properties;
            this.required = required;
            this.additionalProperties = additionalProperties;
        }
    }

    [System.Serializable]
    public class ArgProperties
    {
        [JsonProperty("type")]
        public string type { get; set; }

        [JsonProperty("description")]
        public string description { get; set; }
    }

    [System.Serializable]
    public class Parameters
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
        public FunctionParameters parameter { get; set; }

        public FunctionDefinition(string name, string description, FunctionParameters parameter)
        {
            this.name = name;
            this.description = description;
            this.parameter = parameter;
        }
    }

    [System.Serializable]
    public class ChatMessage
    {
        [JsonProperty("role")]
        public string role { get; set; } // system, user, function

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

    private IEnumerator SendAsync(ChatRequest chatRequest, UnityAction<string> callbackOnSuccess, UnityAction<string> callbackOnFail, bool verbose = false)
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

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string responseText = request.downloadHandler.text;
                if (verbose)
                    Debug.Log("Received response: " + responseText);

                callbackOnSuccess(responseText);
            }
            else
            {
                if (verbose)
                    Debug.LogError("Error: " + request.error + " | " + request.downloadHandler.text);

                callbackOnFail(request.error);
            }
        }
    }

    public void StartConversationAsync(string systemMessage, string userMessage, string model, bool enableFunctionCalling, UnityAction<string> callbackOnSuccess, UnityAction<string> callbackOnFail, bool verbose = false)
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

        UnityAction<string> newCallbackOnSuccess = new UnityAction<string>(response =>
        {
            ChatResponse chatResponse = JsonConvert.DeserializeObject<ChatResponse>(response);

            if (chatResponse != null && chatResponse.choices != null && chatResponse.choices.Count > 0)
            {
                ChatMessage responseMessage = chatResponse.choices[0].message;
                conversationHistory.Add(responseMessage);

                if (responseMessage.FunctionCall != null && enableFunctionCalling)
                {
                    ContinueConversationWithFunctionResultAsync(conversationHistory, model, callbackOnSuccess, callbackOnFail, verbose);
                }
                else
                {
                    if (verbose)
                        Debug.Log("Assistant response: " + responseMessage.content);

                    callbackOnSuccess(responseMessage.content);
                }
            }
            else
            {
                callbackOnFail("Assistant didn't respond in StartConversationAsync.");
            }
        });

        StartCoroutine(SendAsync(initialRequest, newCallbackOnSuccess, callbackOnFail, verbose));
    }

    private void ContinueConversationWithFunctionResultAsync(List<ChatMessage> conversationHistory, string model, UnityAction<string> callbackOnSuccess, UnityAction<string> callbackOnFail, bool verbose = false)
    {
        ChatRequest newRequest = new ChatRequest
        {
            model = model,
            messages = conversationHistory,
            Functions = functionDefinitions.ToList(),
        };

        UnityAction<string> newCallbackOnSuccess = new UnityAction<string>(response =>
        {
            ChatResponse chatResponse = JsonConvert.DeserializeObject<ChatResponse>(response);

            if (chatResponse != null && chatResponse.choices != null && chatResponse.choices.Count > 0)
            {
                ChatMessage responseMessage = chatResponse.choices[0].message;
                conversationHistory.Add(responseMessage);

                if (responseMessage.FunctionCall != null)
                {
                    CallFunctionAsync(conversationHistory, responseMessage, model, callbackOnSuccess, callbackOnFail, verbose);
                }
                else
                {
                    if (verbose)
                        Debug.Log("Assistant response: " + responseMessage.content);

                    callbackOnSuccess(responseMessage.content);
                }
            }
            else
            {
                callbackOnFail("Assistant didn't respond in ContinueConversationWithFunctionResultAsync.");
            }
        });

        StartCoroutine(SendAsync(newRequest, newCallbackOnSuccess, callbackOnFail, verbose));
    }

    private void CallFunctionAsync(List<ChatMessage> conversationHistory, ChatMessage message, string model, UnityAction<string> callbackOnSuccess, UnityAction<string> callbackOnFail, bool verbose = false)
    {
        Dictionary<string, string> args = JsonConvert.DeserializeObject<Dictionary<string, string>>(message.FunctionCall.arguments);

        if (functionMapping.ContainsKey(message.FunctionCall.name))
        {
            if (verbose)
                Debug.Log("LLM called \"" + message.FunctionCall.name + "\" with keys {" + string.Join(" ", args.Keys) + "} and values {" + string.Join(" ", args.Values) + "}.");

            string result = functionMapping[message.FunctionCall.name](args);

            if (verbose)
                Debug.Log("Got result: " + result);

            ChatMessage functionResultMessage = new ChatMessage
            {
                role = "function",
                content = result
            };

            conversationHistory.Add(functionResultMessage);

            ContinueConversationWithFunctionResultAsync(conversationHistory, model, callbackOnSuccess, callbackOnFail, verbose);
        }
        else
        {
            if (verbose)
                Debug.Log("LLM called \"" + message.FunctionCall.name + "\" with keys {" + string.Join(" ", args.Keys) + "} and values {" + string.Join(" ", args.Values) + "} but it does not exist.");

            callbackOnFail("The function " + message.FunctionCall.name + " does not exist.");
        }
    }
}
