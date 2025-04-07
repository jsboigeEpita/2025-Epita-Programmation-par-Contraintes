using UnityEngine;

public class Item : MonoBehaviour
{
    public BoxCollider itemCollider;

    public void Awake()
    {
        itemCollider = GetComponent<BoxCollider>();
        if (itemCollider == null)
        {
            Debug.LogError(this.name + " has no collider.");
        }
    }
}
