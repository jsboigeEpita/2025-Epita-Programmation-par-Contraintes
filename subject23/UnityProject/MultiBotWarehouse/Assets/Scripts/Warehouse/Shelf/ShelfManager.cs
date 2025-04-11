using System.Linq;
using UnityEngine;

public class ShelfManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;
    public ShelvingUnit shelvingUnit;

    [Header("Prefab")]
    [SerializeField]
    public int furnitureIndex;
    [SerializeField]
    private GameObject furniturePrefab;

    private void Awake()
    {
        furniturePrefab = furnitures.furnitures[furnitureIndex];
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

                shelvingUnit.DoOneRotation(0.1f);
            }
            else if (robotManager.currentItem != null)
            {
                if (robotManager.currentItem.itemIndexes == null)
                {
                    if (shelvingUnit.items.Where(ele => ele != null).Count() < shelvingUnit.items.Count)
                    {
                        while (shelvingUnit.currentShelf.currentItem != null)
                            shelvingUnit.DoOneRotation(0.1f);
                    }
                    else
                    {
                        if (shelvingUnit.currentShelf.currentItem != null)
                        {
                            Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with an object but an object was already here.");
                            return;
                        }
                    }
                }
                else
                {
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with a box.");
                }
            }
        }
    }
}
