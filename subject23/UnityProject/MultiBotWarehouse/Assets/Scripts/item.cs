using UnityEngine;

public class item : MonoBehaviour
{
    private Collider curr_collider;

    private void OnTriggerEnter(Collider other)
    {
        if (other.name == "item")
        {
            curr_collider = other;
            other.transform.SetParent(this.transform);
        }
    }

    public void Disable()
    {
        if (curr_collider != null)
            curr_collider.transform.SetParent(this.transform.parent.parent);
        curr_collider = null;
    }
}
