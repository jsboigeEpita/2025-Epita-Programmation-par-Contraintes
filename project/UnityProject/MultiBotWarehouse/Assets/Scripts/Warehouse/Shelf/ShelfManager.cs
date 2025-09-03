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
                if (shelvingUnit.items.Where(ele => ele != null).Count() != 0)
                {
                    if (robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Shelf)
                    {
                        while (shelvingUnit.currentShelf.currentItem == null)
                            shelvingUnit.DoOneRotation(0);

                        shelvingUnit.currentShelf.PutOnRobot(robotManager);

                        shelvingUnit.DoOneRotation(0.1f);
                    }
                }
                else
                {
                    Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " without any objects and there was nothing.");
                    return;
                }
            }
            else if (robotManager.currentItem != null)
            {
                if (robotManager.currentItem.itemIndexes == null)
                {
                    if (shelvingUnit.items.Where(ele => ele != null).Count() < shelvingUnit.items.Count)
                    {
                        if (!robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Input)
                        {
                            while (shelvingUnit.currentShelf.currentItem != null)
                                shelvingUnit.DoOneRotation(0.1f);

                            string name = robotManager.currentItem.gameObject.name;

                            shelvingUnit.currentShelf.TakeFromRobot(robotManager);

                            if (name.Contains(shelvingUnit.currentShelf.itemName))
                                shelvingUnit.DoOneRotation(0.1f);
                        }
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
