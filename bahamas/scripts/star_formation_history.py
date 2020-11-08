"""
Plots the star formation history. Modified version of the script in the
github.com/swiftsim/swiftsimio-examples repository.
"""
import matplotlib

import unyt

import matplotlib.pyplot as plt
import numpy as np
import sys

from swiftsimio import load

from load_sfh_data import read_obs_data

sfr_output_units = unyt.msun / (unyt.year * unyt.Mpc ** 3)

from swiftpipeline.argumentparser import ScriptArgumentParser

arguments = ScriptArgumentParser(
    description="Creates a star formation history plot, with added observational data."
)

snapshot_filenames = [
    f"{directory}/{snapshot}"
    for directory, snapshot in zip(arguments.directory_list, arguments.snapshot_list)
]

sfr_filenames = [f"{directory}/SFR.txt" for directory in arguments.directory_list]

names = arguments.name_list
output_path = arguments.output_directory

plt.style.use(arguments.stylesheet_location)

simulation_lines = []
simulation_labels = []

fig, ax = plt.subplots()

ax.loglog()

for snapshot_filename, sfr_filename, name in zip(
    snapshot_filenames, sfr_filenames, names
):
    data = np.genfromtxt(sfr_filename).T

    snapshot = load(snapshot_filename)
    units = snapshot.units
    boxsize = snapshot.metadata.boxsize
    box_volume = boxsize[0] * boxsize[1] * boxsize[2]

    sfr_units = snapshot.gas.star_formation_rates.units

    # a, Redshift, SFR
    scale_factor = data[2]
    redshift = data[3]
    star_formation_rate = (data[7] * sfr_units / box_volume).to(sfr_output_units)

    # High z-order as we always want these to be on top of the observations
    simulation_lines.append(
        ax.plot(scale_factor, star_formation_rate.value, zorder=10000)[0]
    )
    simulation_labels.append(name)

# Observational data plotting

observational_data = read_obs_data(
    f"{arguments.config.config_directory}/{arguments.config.observational_data_directory}"
    "/data/StarFormationRateHistory/raw"
)

observation_lines = []
observation_labels = []

for index, observation in enumerate(observational_data):
    if observation.fitting_formula:
        if observation.description == "EAGLE-25 REF":
            observation_lines.append(
                ax.plot(
                    observation.scale_factor,
                    observation.sfr,
                    label=observation.description,
                    color="aquamarine",
                    zorder=-10000,
                    linewidth=1,
                    alpha=0.5,
                )[0]
            )
        else:
            observation_lines.append(
                ax.plot(
                    observation.scale_factor,
                    observation.sfr,
                    label=observation.description,
                    color="grey",
                    linewidth=1,
                    zorder=-1000,
                )[0]
            )
    else:
        observation_lines.append(
            ax.errorbar(
                observation.scale_factor,
                observation.sfr,
                observation.error,
                label=observation.description,
                linestyle="none",
                marker="o",
                elinewidth=0.5,
                markeredgecolor="none",
                markersize=2,
                zorder=index,  # Required to have line and blob at same zodrer
            )
        )
    observation_labels.append(observation.description)


ax.set_xlabel("Redshift $z$")
ax.set_ylabel(r"SFR Density $\dot{\rho}_*$ [M$_\odot$ yr$^{-1}$ Mpc$^{-3}$]")


redshift_ticks = np.array([0.0, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0])
redshift_labels = [
    "$0$",
    "$0.2$",
    "$0.5$",
    "$1$",
    "$2$",
    "$3$",
    "$5$",
    "$10$",
    "$20$",
    "$50$",
    "$100$",
]
a_ticks = 1.0 / (redshift_ticks + 1.0)

ax.set_xticks(a_ticks)
ax.set_xticklabels(redshift_labels)
ax.tick_params(axis="x", which="minor", bottom=False)

ax.set_xlim(1.02, 0.07)
ax.set_ylim(1.8e-4, 1.7)

observation_legend = ax.legend(
    observation_lines, observation_labels, markerfirst=True, loc=3, fontsize=4, ncol=2
)

simulation_legend = ax.legend(
    simulation_lines, simulation_labels, markerfirst=False, loc="upper right"
)

ax.add_artist(observation_legend)

fig.savefig(f"{output_path}/star_formation_history.png")
