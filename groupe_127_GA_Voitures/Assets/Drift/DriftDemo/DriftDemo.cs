using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

public class DriftDemo : MonoBehaviour
{
    [SerializeField] float SIMULATION_SPEED;
    [SerializeField] GameObject car_prefab;
    [HideInInspector] public int nb_cars_alives; // this is decremented by cars when they die
    private CameraScriptDrift cameraScript;
    private CarControllerDrift demoCar;
    private Transform spawnPoint;

    private void Start()
    {
        this.demoCar = null;
        Time.timeScale = this.SIMULATION_SPEED;
        this.cameraScript = GameObject.Find("Main Camera").GetComponent<CameraScriptDrift>();
        this.GetSpawnPoint();
    }

    private void FixedUpdate()
    {
        if (this.nb_cars_alives <= 0)
        {
            this.CleanLastEpoch();
            this.InstantiateStartCar();
            return;
        }
        if (this.demoCar != null)
        {
            this.demoCar.Move();
        }
    }

    private void CleanLastEpoch()
    {
        Destroy(this.demoCar);
        this.demoCar = null;
    }


    // START METHODS
    private void InstantiateStartCar()
    {
        this.demoCar = Instantiate(this.car_prefab, this.spawnPoint.position, this.spawnPoint.rotation).GetComponent<CarControllerDrift>();
        this.demoCar.network = NN_Utilities.LoadNN("GASGASGAS");
        this.nb_cars_alives = 1;
        this.cameraScript.toFollow = this.demoCar.gameObject;
    }

    private void GetSpawnPoint()
    {
        this.spawnPoint = GameObject.Find("SpawnPoint").transform;
    }

    public void LoadMainMenu()
    {
        SceneManager.LoadScene("Menu");
    }
}
