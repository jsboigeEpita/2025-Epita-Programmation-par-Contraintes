using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GA_Manager : MonoBehaviour
{
    [SerializeField] int NB_START_POPULATION;
    [SerializeField] int NB_DADS;
    [SerializeField] bool LOAD_NN;
    [SerializeField] string SAVE_FILE;
    [SerializeField] float SIMULATION_SPEED;
    [SerializeField] GameObject car_prefab;
    
    [HideInInspector] public int nb_cars_alives; // this is decremented by cars when they die
    [SerializeField] int max_nb_epochs;
    [SerializeField] int max_ticks_for_epoch;
    private int nb_epochs;
    private int ticks;
    
    List<CarController> cars;
    private Transform spawnPoint;
    private List<Vector3> checkpointsPositions;
    private CameraScript cameraScript;

    // UI TEXTS
    [SerializeField] Text epochText;
    [SerializeField] Text ticksText;
    [SerializeField] Text carsAliveText;
    [SerializeField] Text bestScoreText;
    [SerializeField] Text ticksTakenText;

    private void Start()
    {
        this.PerformStartChecks();
        this.GetCamera();
        this.GetSpawnPoint();
        this.GetCheckpoints();
        this.InstantiateStartCars();
        this.InitUi();
        this.ticks = 0;
    }

    private void FixedUpdate()
    {
        if (this.nb_cars_alives <= 0 || (this.ticks >= this.max_ticks_for_epoch && MenuData.training))
        {
            this.ticks = 0;
            this.InstantiateNewGenCars();
            return;
        }
        foreach (var car in this.cars)
        {
            car.Move();
        }
        this.UpdateUi(-1, this.ticks++, this.nb_cars_alives, -1, -1);
    }

    // EPOCH METHODS
    private void InstantiateNewGenCars()
    {
        this.cameraScript.resetToFollow();
        List<NN> dads = this.getBestNetworks();
        List<NN> new_networks = this.getNewNetworks(dads);
        if (MenuData.training) {
            this.AdaptMaxTicks();
        }
        this.CleanLastEpoch();

        for (int i = 0; i < new_networks.Count; i++)
        {
            GameObject car = Instantiate(this.car_prefab, this.spawnPoint.position, this.spawnPoint.rotation);
            car.GetComponent<CarController>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            car.GetComponent<CarController>().network = new_networks[i].DeepCopy();
            this.cars.Add(car.GetComponent<CarController>());
            car.GetComponent<CarController>().SetSkin(false);
            car.GetComponent<CarController>().demoMode = !MenuData.training;
        }
        this.cars[0].SetSkin(true);
        this.cameraScript.toFollow = this.cars[0].gameObject;
        this.nb_cars_alives = new_networks.Count;
        this.ticks = 0;
        Time.timeScale = this.SIMULATION_SPEED;
    }

    private List<NN> getNewNetworks(List<NN> dads)
    {
        List<NN> new_networks = new List<NN>();
        new_networks.AddRange(dads);
        if (MenuData.training) {
            new_networks.AddRange(GA_Algorithms.two_parents_mutation_top_n_dads(dads, Mathf.Min(this.NB_DADS, 10), 0.5f, 0.5f));
            new_networks.AddRange(GA_Algorithms.basic_mutation(dads, 0.5f, 0.5f));
        }
        return new_networks;
    }

    private List<NN> getBestNetworks()
    {
        foreach(CarController car in this.cars)
        {
            if (car.canMove)
            {
                car.StopMoving();
            }
        }

        this.cars = this.cars.OrderByDescending(x => x.score).ToList();
        if (this.cars[0].score == this.checkpointsPositions.Count) // they already completed the track, so now we go fast boyy
        {
            this.cars = this.cars.OrderByDescending(x => x.score).ThenBy(x => x.ticksTaken).ToList();
            this.UpdateUi(++this.nb_epochs, -1, -1, this.cars[0].score, this.cars[0].ticksTaken);
        }
        else
        {
            this.UpdateUi(++this.nb_epochs, -1, -1, this.cars[0].score, -1);
        }
        NN_Utilities.SaveNN(this.SAVE_FILE, this.cars[0].network);
        List<NN> result = new List<NN>();
        for (int i = 0; i < this.NB_DADS; i++)
        {
            result.Add(this.cars[i].network.DeepCopy());
        }
        return result;
    }

    private void CleanLastEpoch()
    {
        foreach(CarController car in this.cars)
        {
            Destroy(car.gameObject);
        }
        this.cars.Clear();
    }

    // START METHODS
    private void InstantiateStartCars()
    {
        this.cars = new List<CarController>();
        for (int i = 0; i < this.NB_START_POPULATION; i++)
        {
            GameObject car = Instantiate(this.car_prefab, this.spawnPoint.position, this.spawnPoint.rotation);
            car.GetComponent<CarController>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            if (this.LOAD_NN)
            {
                car.GetComponent<CarController>().network = NN_Utilities.LoadNN(this.SAVE_FILE);
            }
            else
            {
                car.GetComponent<CarController>().network = new NN();
                car.GetComponent<CarController>().network.AddLayer(6, 4, ActivationMethod.ReLU);
                car.GetComponent<CarController>().network.AddLayer(4, 2, ActivationMethod.Sigmoid);
                car.GetComponent<CarController>().network.Mutate(1f, 1f);
            }
            this.cars.Add(car.GetComponent<CarController>());
            car.GetComponent<CarController>().SetSkin(false);
            car.GetComponent<CarController>().demoMode = !MenuData.training;
        }
        this.nb_cars_alives = this.NB_START_POPULATION;
        this.cars[0].GetComponent<CarController>().SetSkin(true);
        this.cameraScript.toFollow = this.cars[0].gameObject;
    }

    private void GetSpawnPoint()
    {
        this.spawnPoint = GameObject.Find("SpawnPoint").transform;
    }

    private void GetCheckpoints()
    {
        GameObject checkpoints = GameObject.Find("RoadManager");
        this.checkpointsPositions = checkpoints.GetComponent<SplineRoadCreator>().checkpoints.ConvertAll(x => new Vector3(x.x, x.y, x.z));
    }

    private void GetCamera()
    {
        this.cameraScript = GameObject.Find("Main Camera").GetComponent<CameraScript>();
    }

    public void PerformStartChecks()
    {
        if (!MenuData.training)
        {
            this.NB_START_POPULATION = 1;
            this.NB_DADS = 1;
            this.LOAD_NN = true;
        }
        if (MenuData.training && MenuData.fileName != "" && NN_Utilities.LoadNN(MenuData.fileName) != null)
        {
            this.LOAD_NN = true;
        }
        this.SAVE_FILE = MenuData.fileName;
        if (this.SAVE_FILE == "") // if user forgot to specify a filename
        {
            this.SAVE_FILE = "temp";
            this.LOAD_NN = false;
            MenuData.training = true;
        }
        Time.timeScale = this.SIMULATION_SPEED;
    }

    // UI METHODS
    private void InitUi()
    {
        this.epochText.text = "epoch: 0";
        this.ticksText.text = "ticks: 0";
        this.carsAliveText.text = "cars alive: 0";
        this.bestScoreText.text = "best score: 0";
        this.ticksTakenText.text = "best lap time: NaN";
    }

    private void UpdateUi(int epoch, int ticks, int carsAlive, int bestScore, int ticks_taken)
    {
        if (epoch != -1)
        {
            this.epochText.text = "epoch: " + epoch.ToString();
        }
        if (ticks != -1)
        {
            this.ticksText.text = "ticks: " + ticks.ToString() + " / " + this.max_ticks_for_epoch.ToString();
        }
        if (carsAlive != -1)
        {
            this.carsAliveText.text = "cars alive: " + carsAlive.ToString();
        }
        if (bestScore != -1)
        {
            this.bestScoreText.text = "best score: " + bestScore.ToString();
        }
        if (ticks_taken != -1)
        {
            this.ticksTakenText.text = "best lap time: " + ticks_taken.ToString();
        }
    }

    public void LoadMainMenu()
    {
        SceneManager.LoadScene("Menu");
    }

    // ADAPTIVE TICKS
    private void AdaptMaxTicks()
    {
        if (this.cars[0].score == this.checkpointsPositions.Count)
        {
            this.max_ticks_for_epoch = this.cars[0].ticksTaken;
        }
        else if (this.cars.GetRange(0, 10).ConvertAll(x => x.ticksTaken).Max() == this.max_ticks_for_epoch)
        {
            this.max_ticks_for_epoch += this.max_ticks_for_epoch / 2;
        }
    }
}
