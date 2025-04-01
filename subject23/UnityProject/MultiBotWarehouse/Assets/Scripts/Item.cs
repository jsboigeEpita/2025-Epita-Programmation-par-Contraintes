using UnityEngine;

public class Item : MonoBehaviour
{
    public enum Type
    {
        Wood
    }

    public Type type;
    public Collider itemCollider;

    public void Awake()
    {
        itemCollider = GetComponent<Collider>();
        if (itemCollider == null)
        {
            Debug.LogError(this.name + " has no collider.");
        }
    }
}
