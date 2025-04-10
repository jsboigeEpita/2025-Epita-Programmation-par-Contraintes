using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

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

    private IAsyncEnumerator<string> currentLoop = null;
    private System.Threading.Tasks.ValueTask<bool> currentMoveNextTask;

    private string prompt = 
        "You are a furniture warehouse assistant responsible for taking orders and confirming them with customers. " +
        "You are only allowed to take orders for items that are listed in the furniture list below. " +
        "When a client submits an order, you must produce two separate messages:" +
        "\n\n" +
        "1. **Order Items JSON:**" +
        "\n" +
        "\tOutput a JSON formatted array of strings representing only the items the client ordered that exist in the furniture list. Items not in the furniture list should NOT be included in this JSON array." +
        "\n\n" +
        "2. **Acknowledgement Message:**" +
        "\n" +
        "\tOutput a plain text message that acknowledges the order. In this message, list the items that will be produced (i.e., those that are in the furniture list) and, if applicable, mention any items that the client requested but are not available (i.e., not in the furniture list)." +
        "\n\n" +
        "**Furniture List:**\n" +
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
        "Washing Machine" +
        "\n\n" +
        "**Rules to strictly follow:**" +
        "\n" +
        "- **Do not include any items in the output that are not in the furniture list.**" +
        "\n" +
        "- If the client mentions items not found in the furniture list, exclude them from the JSON order but mention them in your acknowledgment message that they are not available." +
        "\n" +
        "- Output exactly two messages: first the JSON array (with only available items) and second, a plain text message confirming the processed order and listing what items are in the order." +
        "\n" +
        "- Do not produce any extraneous or unrelated output." +
        "\n\n" +
        "**Example:**" +
        "\n" +
        "If the client says: \"I would like to order Bed, Sofa, and Computer.\" Your response should be: *Message 1 (JSON array):* `[\"Bed\", \"Sofa\"]` and *Message 2 (Text):* \"Order received for: Bed, Sofa. Note: 'Computer' is not available.\"" +
        "\n" +
        "Always check the client's order against the furniture list and follow the above rules strictly.";

    private void Update()
    {
        if (inputButton)
        {
            if (currentLoop == null)
            {
                currentLoop = apiInteraction.StartConversation(prompt, inputText, model, false, verbose).GetAsyncEnumerator();
                currentMoveNextTask = currentLoop.MoveNextAsync();
            }

            if (!currentMoveNextTask.IsCompletedSuccessfully)
            {
                return;
            }
            else
            {
                currentMoveNextTask = currentLoop.MoveNextAsync();
            }

            if (currentMoveNextTask.AsTask().Status == TaskStatus.RanToCompletion)
            {
                Debug.Log("Received the following message: " + currentLoop.Current);
                currentLoop.DisposeAsync();
                currentLoop = null;
                inputButton = false;
            }
            else
            {
                Debug.Log("Received the following message: " + currentLoop.Current);
            }
        }
    }
}
