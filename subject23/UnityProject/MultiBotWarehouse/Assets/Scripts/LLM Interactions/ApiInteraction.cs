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

    Task<string> currentLoop = null;
    [SerializeField]
    private bool inputButton = false;
    [SerializeField]
    private string inputText;
    private string systemMessage = "You are a helpful assistant. We provide you the list of functions that you can call\n" +
        "You can call them by using the function name and providing the required arguments in JSON format." +
        "Your goal is to help the user by calling the functions and providing the results.\n" + 
        "You need to evaluate the user input and decide whether to call a function or not and which one to call.\n" +
        "You can call the functions by using the function name and providing the required arguments.\n" +
        "It is your job to decide the parameters to pass to the function.\n" +
        "If you don't want to call any function, just respond with \"END\".\n" +
        "I zqnt you to output the function call in JSON format.\n" +
        "The function call should be in the following format:\n" +
        '{' + "\n" +
        "  \"name\": \"function_name\",\n" +
        "  \"arguments\": {\n" +
        "    \"arg1\": \"value1\",\n" +
        "    \"arg2\": \"value2\"\n" +
        "  }\n" +
        "}\n";

    private void Update()
    {
        if (inputButton)
        {
            if (currentLoop == null)
                currentLoop = StartConversationAsync(systemMessage, inputText, "gpt-4o-mini", true, true);

            if (currentLoop.Status == TaskStatus.RanToCompletion)
            {
                Debug.Log("Received the following message: " + currentLoop.Result);
                currentLoop = null;
                inputButton = false;
            }
        }
    }
    public static Task<string> function1(int a, string b)
    {
        return Task.Run(() =>
        {
            // Simulate some processing
            System.Threading.Thread.Sleep(1000);
            return $"Function 1 called with a: {a}, b: {b}";
        });
    }

    public static Task<string> function1Dico(Dictionary<string, string> args)
    {
        int a = int.Parse(args["a"]);
        string b = args["b"];
        return function1(a, b);
    }

    private static Dictionary<string, Func<Dictionary<string, string>, Task<string>>> functionMapping = new Dictionary<string, Func<Dictionary<string, string>, Task<string>>>    
    {};

    private static List<FunctionDefinition> functionDefinitions = new List<FunctionDefinition>
    ();

    private void Awake()
    {
        functionMapping.Add("function1", function1Dico);

        var properties = new { a = new ArgProperties() { type = "integer", description = "the desc of the first arg" },
            b = new ArgProperties() { type = "string", description = "the desc of the second arg" } };

    
        functionDefinitions.Add(new FunctionDefinition("function1", "This is the first function",
            new FunctionParameters("object", properties, new string[] {"a", "b"}, false)
        ));
    }

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
