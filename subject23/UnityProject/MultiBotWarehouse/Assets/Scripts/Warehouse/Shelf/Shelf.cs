using UnityEngine;

public class Shelf : MonoBehaviour
{
    public Item currentItem;

    private Vector3 storePosition;
    public string itemName;
    private float furnitureScale;

    public void Initialize(Vector3 storePosition, string itemName, float furnitureScale)
    {
        this.storePosition = storePosition;
        this.itemName = itemName;
        this.furnitureScale = furnitureScale;
    }

    public void TakeFromRobot(RobotManager robotManager)
    {
        if (!robotManager.currentItem.gameObject.name.Contains(itemName))
        {
            Debug.LogError(robotManager.name + " arrived to " + this.name + " with an object of the wrong type.");
            return;
        }

        currentItem = robotManager.currentItem;
        robotManager.currentItem = null;

        currentItem.transform.SetParent(this.transform);
        currentItem.transform.localPosition = storePosition;
    }

    public void PutOnRobot(RobotManager robotManager)
    {
        robotManager.currentItem = currentItem;
        currentItem = null;

        robotManager.currentItem.transform.SetParent(robotManager.storeTransform);
        robotManager.currentItem.transform.localPosition = Vector3.zero;
        robotManager.currentItem.transform.localScale = Vector3.one * furnitureScale;
    }
}
