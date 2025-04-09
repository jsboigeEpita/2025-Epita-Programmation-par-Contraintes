using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;

public class PackerManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private PackerInputManager inputManager;
    [SerializeField]
    private PackerOutputManager outputManager;
    [SerializeField]
    private TMP_Text text;
    [SerializeField]
    private Furnitures furnitures;

    private List<Item> buffer;

    private void Awake()
    {
        buffer = new List<Item>();

        inputManager.packerManager = this;
        outputManager.packerManager = this;
    }

    private void Update()
    {
        text.text = string.Join("\n", buffer.Select(ele => furnitures.furnitures[ele.itemIndex].name).ToArray());
    }

    public void AddToBuffer(Item item)
    {
        buffer.Add(item);
    }

    public List<Item> GetBuffer()
    {
        return buffer;
    }
}
