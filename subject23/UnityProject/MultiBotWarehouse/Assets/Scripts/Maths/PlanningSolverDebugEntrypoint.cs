using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using static PlanningSolver;
using static UnityEngine.Rendering.DebugUI.Table;

public class PlanningSolverDebugEntrypoint : MonoBehaviour
{
    [Header("Setup")]
    [SerializeField]
    private int numRobots;
    [SerializeField]
    private List<Job> jobs;
    [SerializeField]
    private IntArrayWrapper[] travelTimes;
    [SerializeField]
    private long horizon = int.MaxValue;
    [SerializeField]
    private bool verbose = true;

    [Header("Button")]
    [SerializeField]
    private bool solveButton = false;


    [System.Serializable]
    public class IntArrayWrapper
    {
        public int[] values;

        public IntArrayWrapper(int[] values)
        {
            this.values = values;
        }
    }

    private void Update()
    {
        if (solveButton)
        {
            int[][] result = Solve(numRobots, jobs.ToArray(), travelTimes.Select(ele => ele.values).ToArray(), horizon, verbose);

            string filePath = Path.Combine(Application.persistentDataPath, "solve.csv");
            Debug.Log("Outputting Solve result to " + filePath);

            using (StreamWriter writer = new StreamWriter(filePath))
            {
                for (int i = 0; i < result.Length; i++)
                {
                    writer.WriteLine(string.Join("\t", result[i]));
                }
            }

            solveButton = false;
        }
    }
}
