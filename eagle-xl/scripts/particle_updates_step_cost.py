"""
Plots the distribution of particle updates vs. step wallclok time
"""

import unyt

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

from swiftpipeline.argumentparser import ScriptArgumentParser
from swiftsimio import load
from glob import glob

# Set the limits of the figure.
update_bounds = [1, 10.0 ** 10.0]  #
wallclock_bounds = [1, 10.0 ** 6.0]  # in ms
bins = 512


def get_data(filename):
    """
    Grabs the data (T in Kelvin and density in mh / cm^3).
    """

    data = np.genfromtxt(filename, skip_footer=5, loose=True, invalid_raise=False).T

    number_of_updates = unyt.unyt_array(data[7], units="dimensionless")
    wallclock_time = unyt.unyt_array(data[-2], units="ms")

    return number_of_updates.value, wallclock_time.value


def make_hist(filename, update_bounds, wallclock_bounds, bins):
    """
    Makes the histogram for filename with bounds as lower, higher
    for the bins and "bins" the number of bins along each dimension.

    Also returns the edges for pcolormesh to use.
    """

    number_of_updates_bins = unyt.unyt_array(
        np.logspace(np.log10(update_bounds[0]), np.log10(update_bounds[1]), bins),
        units="dimensionless",
    )
    wallclock_time_bins = unyt.unyt_array(
        np.logspace(np.log10(wallclock_bounds[0]), np.log10(wallclock_bounds[1]), bins),
        units="ms",
    )

    H, update_edges, wallclock_edges = np.histogram2d(
        *get_data(filename),
        bins=[number_of_updates_bins.value, wallclock_time_bins.value],
    )

    return H.T, update_edges, wallclock_edges


def setup_axes(number_of_simulations: int):
    """
    Creates the figure and axis object. Creates a grid of a x b subplots
    that add up to at least number_of_simulations.
    """

    sqrt_number_of_simulations = np.sqrt(number_of_simulations)
    horizontal_number = int(np.ceil(sqrt_number_of_simulations))
    # Ensure >= number_of_simulations plots in a grid
    vertical_number = int(np.ceil(number_of_simulations / horizontal_number))

    fig, ax = plt.subplots(
        vertical_number, horizontal_number, squeeze=True, sharex=True, sharey=True
    )

    ax = np.array([ax]) if number_of_simulations == 1 else ax

    if horizontal_number * vertical_number > number_of_simulations:
        for axis in ax.flat[number_of_simulations:]:
            axis.axis("off")

    # Set all valid on bottom row to have the horizontal axis label.
    for axis in np.atleast_2d(ax)[:][-1]:
        axis.set_xlabel("# of gas part. updates in step")

    for axis in np.atleast_2d(ax).T[:][0]:
        axis.set_ylabel("Wallclock time for step [ms]")

    ax.flat[0].loglog()

    return fig, ax


def make_single_image(
    filenames,
    names,
    number_of_simulations,
    update_bounds,
    wallclock_bounds,
    bins,
    output_path,
):
    """
    Makes a single plot of rho-T
    """

    fig, ax = setup_axes(number_of_simulations=number_of_simulations)

    hists = []

    for filename in filenames:
        hist, d, T = make_hist(filename, update_bounds, wallclock_bounds, bins)
        hists.append(hist)

    vmax = np.max([np.max(hist) for hist in hists])

    for hist, name, axis in zip(hists, names, ax.flat):
        mappable = axis.pcolormesh(d, T, hist, norm=LogNorm(vmin=1, vmax=vmax))
        axis.text(0.025, 0.975, name, ha="left", va="top", transform=axis.transAxes)

    fig.colorbar(mappable, label="Number of steps", pad=0)

    fig.savefig(f"{output_path}/particle_updates_step_cost.png")

    return


if __name__ == "__main__":
    from swiftpipeline.argumentparser import ScriptArgumentParser

    arguments = ScriptArgumentParser(
        description="Creates a run performance plot: particle updates versus wall-clock time"
    )

    timestep_filenames = [
        glob(f"{directory}/timesteps_*.txt")[0]
        for directory in arguments.directory_list
    ]

    plt.style.use(arguments.stylesheet_location)

    make_single_image(
        filenames=timestep_filenames,
        names=arguments.name_list,
        number_of_simulations=arguments.number_of_inputs,
        update_bounds=update_bounds,
        wallclock_bounds=wallclock_bounds,
        bins=bins,
        output_path=arguments.output_directory,
    )
