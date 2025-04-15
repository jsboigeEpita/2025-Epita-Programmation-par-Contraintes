using System.Collections;
using UnityEngine;

public class SourceManager : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;

    [Header("Settings")]
    [SerializeField]
    private float displayFurnitureScale;
    [SerializeField]
    private float displayRotationSpeed;
    [SerializeField]
    private Vector3 displayOffset;

    [SerializeField]
    private float furnitureScale;
    [SerializeField]
    private Vector3 offset;
    
    [Header("Prefab")]
    [SerializeField]
    public int furnitureIndex;
    [SerializeField]
    private GameObject furniturePrefab;

    private GameObject furniture;

    private void Awake()
    {
        furniturePrefab = furnitures.furnitures[furnitureIndex];
    }

    private void Start()
    {
        furniture = GameObject.Instantiate(furniturePrefab, this.transform);
        Collider furnitureCollider = furniture.GetComponent<Collider>();
        furnitureCollider.enabled = false;
        furniture.transform.localPosition = displayOffset;
        furniture.transform.localScale = Vector3.one * displayFurnitureScale;

        StartCoroutine(RotateFurnitureDisplay(Vector3.up, displayRotationSpeed));
    }

    private IEnumerator RotateFurnitureDisplay(Vector3 axis, float speed)
    {
        while (true)
        {
            transform.Rotate(axis * speed * Time.deltaTime);
            yield return null;
        }
    }

    public void PutOnRobot(RobotManager robotManager)
    {
        robotManager.currentItem = GameObject.Instantiate(furniturePrefab).AddComponent<Item>();
        robotManager.currentItem.itemIndex = furnitureIndex;
        robotManager.currentItem.transform.SetParent(robotManager.storeTransform);
        robotManager.currentItem.transform.localPosition = offset;
        robotManager.currentItem.transform.localScale = Vector3.one * furnitureScale;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Robot")
        {
            RobotManager robotManager = other.gameObject.GetComponentInParent<RobotManager>();

            if (robotManager.currentItem == null)
            {
                if (robotManager.isTaking && robotManager.taskType == PlanningSolver.Task.TaskType.Input)
                    PutOnRobot(robotManager);
            }
            else
            {
                Debug.LogWarning(robotManager.gameObject.name + " arrived to " + this.gameObject.name + " with an object.");

                if (robotManager.currentItem.itemIndex != furnitureIndex)
                {
                    Debug.LogError("And that was really a mistake.");
                    robotManager.RemoveItem();
                    PutOnRobot(robotManager);
                }
            }
        }
    }
}
