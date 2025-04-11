import matplotlib.pyplot as plt

# t-wise values
t_values = [2, 3, 4, 5, 6]

# Number of test cases generated per t-wise strategy
test_case_counts = [51, 318, 1714, 8505, 37450]

# Corresponding coverage percentages (%)
coverage_values = [83, 90, 93, 95, 95]

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot coverage line on primary y-axis
color_coverage = "tab:blue"
ax1.set_xlabel("t-wise Interaction Level", fontsize=12)
ax1.set_ylabel("Coverage (%)", color=color_coverage)
ax1.plot(
    t_values,
    coverage_values,
    marker="o",
    linestyle="-",
    color=color_coverage,
    linewidth=2,
    label="Coverage",
)
ax1.tick_params(axis="y", labelcolor=color_coverage)

# Annotate each point on the line
for i in range(len(t_values)):
    ax1.annotate(
        f"{coverage_values[i]}%",
        xy=(t_values[i], coverage_values[i]),
        textcoords="offset points",
        xytext=(0, -15),
        ha="center",
        fontsize=9,
    )

# Create second y-axis for test case count as bars
ax2 = ax1.twinx()
color_tests = "tab:red"
ax2.set_ylabel("Total Number of Test Cases", color=color_tests)
bars = ax2.bar(
    t_values,
    test_case_counts,
    alpha=0.3,
    width=0.6,
    color=color_tests,
    label="Number of Tests",
)
ax2.tick_params(axis="y", labelcolor=color_tests)

# Add annotations above each bar
for rect in bars:
    height = rect.get_height()
    ax2.annotate(
        f"{height}",
        xy=(rect.get_x() + rect.get_width() / 2.0, height),
        xytext=(0, 3),  # offset text slightly above bar top
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
    )

# Title and layout adjustments
plt.title("Test Coverage vs t-wise Interaction Level", fontsize=14)
fig.tight_layout()
plt.grid(True)  # grid underlines for better readability

plt.show()
