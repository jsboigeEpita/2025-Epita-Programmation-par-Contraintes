using System.Collections.Generic;
using UnityEngine;

public class Item : MonoBehaviour
{
    public BoxCollider itemCollider;
    public int itemIndex;
    public List<int> itemIndexes;

    public void Awake()
    {
        itemCollider = GetComponent<BoxCollider>();
        if (itemCollider == null)
        {
            Debug.LogError(this.name + " has no collider.");
        }
    }
}
