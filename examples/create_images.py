import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), '..')))

if True:
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.neighbors import KernelDensity
    from tensorflow.keras.datasets import mnist

    from data.data_handler import ProcessedNNHandler
    from definitions import DATA_PATH
    from evaluation.create_plot import save_plot


def configure_plt():
    plt.rc('font', size=14)
    plt.rc('axes', titlesize=14)
    plt.rc('axes', labelsize=14)
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)
    plt.rc('legend', fontsize=14)
    plt.rc('figure', titlesize=14)


def plot_mnist_samples(width: int = 6, height: int = 2):
    (x_train, y_train), (_, _) = mnist.load_data()
    fig, axs = plt.subplots(height, width, figsize=(width, height))
    for i in range(height):
        for j in range(width):
            first_image = x_train[j + width * i + 120]
            first_image = np.array(first_image, dtype='float')
            pixels = first_image.reshape((28, 28))
            axs[i, j].imshow(pixels, cmap='gray')

    for ax in axs.flat:
        ax.label_outer()

    plt.subplots_adjust(wspace=0.2, hspace=0.2)


def plot_kernels():
    fig, ax = plt.subplots(figsize=(8, 4),
                           subplot_kw={'facecolor': '#F4F4F4',
                                       'axisbelow': True})
    ax.grid(color='white', linestyle='-', linewidth=2)
    for spine in ax.spines.values():
        spine.set_color('#BBBBBB')

    X_src = np.zeros((1, 1))
    x_grid = np.linspace(-3, 3, 1000)

    for kernel in ['gaussian', 'tophat', 'exponential', 'epanechnikov', 'linear', 'cosine']:
        log_dens = KernelDensity(kernel=kernel).fit(
            X_src).score_samples(x_grid[:, None])
        if kernel == 'epanechnikov':
            ax.plot(x_grid, np.exp(log_dens), lw=6, alpha=0.8, label=kernel)
        else:
            ax.plot(x_grid, np.exp(log_dens), lw=3, alpha=0.5, label=kernel)
    ax.set_ylim(0, 1.05)
    ax.set_xlim(-2.9, 2.9)
    ax.legend()


def plot_histogram(path: str):
    processed_nn: ProcessedNNHandler = ProcessedNNHandler(DATA_PATH + path)
    samples: np.array = processed_nn.get_all_samples()
    z_values: np.array = np.zeros(samples.shape[0])
    for i, sample in enumerate(samples):
        z_values[i] = sample[2]
    z_values = z_values.reshape(-1, 1)

    slots: int = 50
    x_grid = np.linspace(-1.2, 1.2, int(slots * 1.2 * 4.0))
    fig, ax = plt.subplots()
    for bandwidth in [0.05, 0.18, 0.5]:
        pdf = KernelDensity(kernel='epanechnikov', bandwidth=bandwidth).fit(
            z_values).score_samples(x_grid[:, None])
        ax.plot(x_grid, np.exp(pdf), linewidth=2, alpha=0.6,
                label='bandwidth=%.2f' % bandwidth)

    ax.hist(z_values, slots, facecolor='gray',
            histtype='stepfilled', alpha=0.4, density=True)
    ax.legend(loc='upper right')
    ax.set_xlim(-1.2, 1.2)


configure_plt()

plot_mnist_samples()
save_plot('mnist')

plt.show()
