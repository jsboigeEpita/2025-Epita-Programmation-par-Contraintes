using UnityEngine;
using Google.OrTools.LinearSolver;
using Google.OrTools.Sat;
using System;

public class OrToolsTest : MonoBehaviour
{
    public class VarArraySolutionPrinter : CpSolverSolutionCallback
    {
        public VarArraySolutionPrinter(IntVar[] variables)
        {
            variables_ = variables;
        }

        public override void OnSolutionCallback()
        {
            {
                Console.WriteLine(String.Format("Solution #{0}: time = {1:F2} s", solution_count_, WallTime()));
                foreach (IntVar v in variables_)
                {
                    Console.WriteLine(String.Format("  {0} = {1}", v.ToString(), Value(v)));
                }
                solution_count_++;
            }
        }

        public int SolutionCount()
        {
            return solution_count_;
        }

        private int solution_count_;
        private IntVar[] variables_;
    }

    void Start()
    {
        /*CpModel model = new CpModel();

        Solver solver = Solver.CreateSolver("GLOP");
        if (solver is null)
        {
            Debug.Log("Could not create solver GLOP");
            return;
        }

        // Create the variables x and y.
        Variable x = solver.MakeNumVar(0.0, 1.0, "x");
        Variable y = solver.MakeNumVar(0.0, 2.0, "y");

        Debug.Log("Number of variables = " + solver.NumVariables());

        // Create a linear constraint, x + y <= 2.
        Google.OrTools.LinearSolver.Constraint constraint = solver.MakeConstraint(double.NegativeInfinity, 2.0, "constraint");
        constraint.SetCoefficient(x, 1);
        constraint.SetCoefficient(y, 1);

        Debug.Log("Number of constraints = " + solver.NumConstraints());

        // Create the objective function, 3 * x + y.
        Objective objective = solver.Objective();
        objective.SetCoefficient(x, 3);
        objective.SetCoefficient(y, 1);
        objective.SetMaximization();

        Debug.Log("Solving with " + solver.ToString());
        Solver.ResultStatus resultStatus = solver.Solve();
        Debug.Log("Status: " + resultStatus);
        if (resultStatus != Solver.ResultStatus.OPTIMAL)
        {
            Debug.Log("The problem does not have an optimal solution!");
            if (resultStatus == Solver.ResultStatus.FEASIBLE)
            {
                Debug.Log("A potentially suboptimal solution was found");
            }
            else
            {
                Debug.Log("The solver could not solve the problem.");
                return;
            }
        }

        Debug.Log("Solution:");
        Debug.Log("Objective value = " + solver.Objective().Value());
        Debug.Log("x = " + x.SolutionValue());
        Debug.Log("y = " + y.SolutionValue());*//*

        // Creates the model.
        CpModel model = new CpModel();

        // Creates the variables.
        int num_vals = 3;

        IntVar x = model.NewIntVar(0, num_vals - 1, "x");
        IntVar y = model.NewIntVar(0, num_vals - 1, "y");
        IntVar z = model.NewIntVar(0, num_vals - 1, "z");

        // Creates the constraints.
        model.Add(x != y);

        // Creates a solver and solves the model.
        CpSolver solver = new CpSolver();
        CpSolverStatus status = solver.Solve(model);

        if (status == CpSolverStatus.Optimal || status == CpSolverStatus.Feasible)
        {
            Debug.Log("x = " + solver.Value(x));
            Debug.Log("y = " + solver.Value(y));
            Debug.Log("z = " + solver.Value(z));
        }
        else
        {
            Debug.Log("No solution found.");
        }*/

        // Creates the model.
        CpModel model = new CpModel();

        // Creates the variables.
        int num_vals = 3;

        IntVar x = model.NewIntVar(0, num_vals - 1, "x");
        IntVar y = model.NewIntVar(0, num_vals - 1, "y");
        IntVar z = model.NewIntVar(0, num_vals - 1, "z");

        // Adds a different constraint.
        model.Add(x != y);

        // Creates a solver and solves the model.
        CpSolver solver = new CpSolver();
        VarArraySolutionPrinter cb = new VarArraySolutionPrinter(new IntVar[] { x, y, z });
        // Search for all solutions.
        solver.StringParameters = "enumerate_all_solutions:true";
        // And solve.
        solver.SolveWithSolutionCallback(model, cb);

        Debug.Log($"Number of solutions found: {cb.SolutionCount()}");
    }
}
