using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Unity.VisualScripting;
using UnityEngine;
using static ApiInteraction;

public class ClientOrderInteraction : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private ApiInteraction apiInteraction;

    [Header("Settings")]
    [SerializeField]
    private string model;
    [SerializeField]
    private bool verbose;

    [Header("Debug")]
    [SerializeField]
    private bool inputButton = false;
    [SerializeField]
    private string inputText;
    [SerializeField]
    private List<string> orders;

    private Task<string> currentLoop = null;

    [System.Serializable]
    public class ResultOrder
    {
        [JsonProperty("order")]
        public List<string> order { get; set; }

        [JsonProperty("message")]
        public string message { get; set; }
    }

    private string prompt =
    "You are a furniture warehouse assistant who takes orders and confirms them with customers. Only items from the furniture list below may be accepted.\n" +
    "When a client places an order, output exactly two messages:\n" +
    "1. **JSON Order:**\n" +
    "\tA JSON array of strings containing only the items from the order that exist in the furniture list.\n" +
    "2. **Acknowledgement Message:**\n" +
    "\tA plain text message that confirms the items being produced (those in the furniture list) and mentions any requested items that are not available.\n" +
    "** Furniture List:**\n" +
    "Air Hockey\n" +
    "Bathroom Bin\n" +
    "Bed\n" +
    "Office Bin\n" +
    "Camera\n" +
    "Large Closet\n" +
    "Medium Closet\n" +
    "Coffee Machine\n" +
    "Coffee Table\n" +
    "Dresser\n" +
    "Fridge\n" +
    "Kitchen Chair\n" +
    "Kitchen Sink\n" +
    "Kitchen Table\n" +
    "Table Lamp\n" +
    "Lamp\n" +
    "Lounge Chair\n" +
    "Microwave Oven\n" +
    "Piano\n" +
    "Office Table\n" +
    "Cat Scratching Post\n" +
    "Sofa\n" +
    "Toy Car\n" +
    "Chalk Board\n" +
    "Washing Machine\n" +
    "**Rules:**\n" +
    "- Do not include items not in the furniture list in the JSON order.\n" +
    "- Exclude unavailable items from the JSON but note them in the acknowledgement message.\n" +
    "- Output only the two required messages and no additional text.\n" +
    "- If the client requests \"random items\", \"random furniture\", or uses similar wording, choose random valid items from the furniture list to include in the order.\n" +
    "  If he doesn't precise the number of objects to generate, chose a random number between 1 and 10 of them to output in the order list\n" +
    "  If a random number of objects is requested, feel free to repeat some items in the \"order\" array.\n" +
    "- Output only a single valid JSON object with keys \"order\" and \"message\", and no extra explanation or markdown.\n" +
    "** Example:**\n" +
    "If the client says: \"I would like to order 2 Bed, a Sofa, and Computer.\"\n" +
    "Your output should be formatted as follows:\n" +
    '{' + " \"order\": [\"Bed\", \"Bed\", \"Sofa\"], \"message\": \"Order received for: Bed, Sofa. Note: 'Computer' is not available.\" }" +
    "If the client says: \"I would like to order 2 items\"\n" +
    "Your output should be formatted as follows:\n" +
    '{' + " \"order\": [\"Bed\", \"Lamp\"], \"message\": \"Order received for 2 items\" }" +
    "If the client says: \"I would like to order items\"\n" +
    "Your output should be formatted as follows:\n" +
    '{' + " \"order\": [\"Office Table\", \"Cat Scratching Post\", \"Toy Car\", \"Dresser\", \"Piano\"], \"message\": \"Order received for a number of items.\" }";

    private void Update()
    {
        if (inputButton)
        {
            if (currentLoop == null)
                currentLoop = apiInteraction.StartConversationAsync(prompt, inputText, model, false, verbose);

            if (currentLoop.Status == TaskStatus.RanToCompletion)
            {
                Debug.Log("Received the following message: " + currentLoop.Result);
                currentLoop = null;
                inputButton = false;
            }
        }
    }

    public string[][] GetRandomOrders()
    {
        return orders.Select(ele => JsonConvert.DeserializeObject<ResultOrder>(ele).order.ToArray()).ToArray();
    }

    /*public string[][] GetRandomOrders(int amount, bool verbose = true)
    {
        string[][] orders = new string[amount][];

        for (int i = 0; i < amount; i++)
        {
            UniTask.Run(async () =>
            {
                return await apiInteraction.StartConversationAsync(prompt, inputText, model, false, verbose);
            }).ContinueWith(result =>
            {
                orders[i] = JsonConvert.DeserializeObject<ResultOrder>(result).order.ToArray();
            });
        }

        return orders;
    }*/
}
