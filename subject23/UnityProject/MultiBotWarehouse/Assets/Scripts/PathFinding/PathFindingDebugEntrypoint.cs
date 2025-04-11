using System.IO;
using UnityEngine;
using static PathFindingCppWrapper;

public class PathFindingDebugEntrypoint : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private AgentInfo[] agentInfoArg;
    [SerializeField]
    private int count;
    [SerializeField]
    private string path;

    [Header("Button")]
    [SerializeField]
    private bool tryButton = false;

    private void Update()
    {
        if (tryButton)
        {
            IndexedPoint[] result = NextStep(agentInfoArg, count, path);

            string filePath = Path.Combine(Application.persistentDataPath, "pathfinding.csv");
            Debug.Log("Outputting Solve result to " + filePath);

            using (StreamWriter writer = new StreamWriter(filePath))
            {
                for (int i = 0; i < result.Length; i++)
                {
                    writer.WriteLine(result[i].id + ": " + result[i].point.x + "," + result[i].point.y);
                }
            }

            tryButton = false;
        }
    }
}
