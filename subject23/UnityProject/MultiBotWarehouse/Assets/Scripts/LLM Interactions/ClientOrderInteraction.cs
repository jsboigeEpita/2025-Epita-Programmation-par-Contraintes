using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Threading.Tasks;
using Google.Protobuf.WellKnownTypes;
using NUnit.Framework;
using Unity.Burst.Intrinsics;
using Unity.VisualScripting;
using UnityEditor.Experimental.GraphView;
using UnityEditor.PackageManager;
using UnityEngine;
using static UnityEditor.Rendering.CameraUI;
using static UnityEngine.InputManagerEntry;
using static UnityEngine.InputSystem.Controls.AxisControl;
using static UnityEngine.Rendering.DebugUI;

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

    private Task<string> currentLoop = null;
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
        "- The client can ask to get random things.\n" +
        "** Example:**\n" +
        "If the client says: \"I would like to order Bed, Sofa, and Computer.\"\n" +
        "Your output should be formatted as follows:\n" +
        "{ \"order\": [\"Bed\", \"Sofa\"], \"message\": \"Order received for: Bed, Sofa. Note: 'Computer' is not available.\" }";

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
}
