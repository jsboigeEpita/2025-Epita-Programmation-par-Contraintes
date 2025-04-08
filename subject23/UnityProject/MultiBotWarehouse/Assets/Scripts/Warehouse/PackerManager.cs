using UnityEngine;

public class PackerManager : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem != null)
            {
                robotManager.RemoveItem();
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without an object.");
            }
        }
    }
}
