using TMPro;
using UnityEngine;
using UnityEngine.Events;

public class SummaryInteraction : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private ApiInteraction apiInteraction;
    [SerializeField]
    private Warehouse warehouse;
    [SerializeField]
    private TMP_InputField inputField;
    [SerializeField]
    private TMP_InputField outputField;

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

    private string prompt = "You are a helpful assistant. We provide you the list of functions that you can call\n" +
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
            UnityAction<string> callbackOnSuccess = new UnityAction<string>(str =>
            {
                Debug.Log(this.name + " received message: " + str);
            });

            UnityAction<string> callbackOnFail = new UnityAction<string>(str =>
            {
                Debug.Log(this.name + " received error: " + str);
            });

            apiInteraction.StartConversationAsync(prompt, inputText, model, false, callbackOnSuccess, callbackOnFail, verbose);

            inputButton = false;
        }
    }

    public void OnClickSubmitButton()
    {
        UnityAction<string> callbackOnSuccess = new UnityAction<string>(str =>
        {
            outputField.text = str;
        });

        UnityAction<string> callbackOnFail = new UnityAction<string>(str =>
        {
            Debug.Log(this.name + " received error: " + str);
        });

        apiInteraction.StartConversationAsync(prompt, inputField.text, model, true, callbackOnSuccess, callbackOnFail, verbose);
    }

    public void OnClickClearButton()
    {
        inputField.text = "";
        outputField.text = "";
    }
}
