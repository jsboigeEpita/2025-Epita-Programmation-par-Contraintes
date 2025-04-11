using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Splines;
using UnityEngine.UI;

public static class MenuData {
    public static String fileName;
    public static bool training;
}

public class MenuManager : MonoBehaviour
{
    [SerializeField] Dropdown mapSelection;
    [SerializeField] Toggle trainingToggle;
    [SerializeField] InputField fileNameInput;
    [SerializeField] List<SplineContainer> maps;
    private SplineRoadCreator roadCreator;

    void Start()
    {
        this.roadCreator = GameObject.Find("RoadManager").GetComponent<SplineRoadCreator>();
        this.roadCreator.CreateMenuSpline(this.maps[0].Spline);
    }

    public void onMapSelectionChange()
    {
        this.roadCreator.DestroyMenuSpline();
        int index = this.mapSelection.value;
        Spline selectedMap = this.maps[index].Spline;
        this.roadCreator.CreateMenuSpline(selectedMap);
    }

    public void onStart()
    {
        MenuData.fileName = this.fileNameInput.text;
        MenuData.training = this.trainingToggle.isOn;
        switch (this.mapSelection.value)
        {
            case 0:
                SceneManager.LoadScene("Basic_0");
                break;
            case 1:
                SceneManager.LoadScene("Basic_1");
                break;
            case 2:
                SceneManager.LoadScene("Wind_0");
                break;
            case 3:
                SceneManager.LoadScene("Wind_1");
                break;
            case 4:
                SceneManager.LoadScene("DriftDemo");
                break;
            default:
                break;
        }
    }
}
