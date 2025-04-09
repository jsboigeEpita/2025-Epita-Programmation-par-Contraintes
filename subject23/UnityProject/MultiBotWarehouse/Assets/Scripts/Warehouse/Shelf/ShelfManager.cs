using UnityEngine;

public class ShelfManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;

    [Header("Prefab")]
    [SerializeField]
    private int furnitureIndex;
    [SerializeField]
    private GameObject furniturePrefab;

    private ShelvingUnit shelvingUnit;

    private void Awake()
    {
        furniturePrefab = furnitures.furnitures[furnitureIndex];

        shelvingUnit = GetComponent<ShelvingUnit>();
        shelvingUnit.itemGameObject = furniturePrefab;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem == null)
            {
                if (shelvingUnit.currentShelf.currentItem == null)
                {
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without any objects.");
                    return;
                }

                shelvingUnit.currentShelf.PutOnRobot(robotManager);
            }
            else if (robotManager.currentItem != null)
            {
                if (shelvingUnit.currentShelf.currentItem != null)
                {
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with an object but an object was already here.");
                    return;
                }
                if (robotManager.currentItem.itemIndexes == null)
                    shelvingUnit.currentShelf.TakeFromRobot(robotManager);
                else
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with a box.");
            }
        }
    }
}
