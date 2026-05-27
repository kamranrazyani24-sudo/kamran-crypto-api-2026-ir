import matplotlib.pyplot as plt

def save_dummy_chart(path="chart.png"):
    plt.figure(figsize=(8, 4))
    plt.plot([1, 2, 3, 2, 4, 3])
    plt.title("Pattern Chart")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path
