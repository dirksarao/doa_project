# FPGA FFT Cross-Correlation Visualizer

This Python script interfaces with a Red Pitaya FPGA board to perform real-time FFT analysis and cross-correlation between two input channels. It continuously reads FFT snapshot data, computes the cross-correlation between the channels, and visualizes the magnitude and phase of the result using Matplotlib.

---

## 🧠 Features

- Real-time snapshot reading from FPGA
- Cross-correlation of two FFT outputs
- Phase difference analysis using:
  - Direct FFT bin comparison
  - Peak of cross-correlation
- Interactive plotting of:
  - Magnitude of cross-correlation
  - Phase of cross-correlation
- Configurable analysis bin (auto or manual)
- Graceful shutdown with `Ctrl+C`
- Clean and informative command-line output

---

## 🚀 Usage

- Clone the repository or copy the script to your working directory.
- Set the path to the desired FPGA .fpg bitstream file.
- Run the script: python3 fft_cross_correlation.py

The script will:

- Upload the bitstream to the FPGA
- Arm and read from a snapshot block
- Compute and accumulate FFT cross-correlations
- Print phase difference information to the console
- Update interactive plots of magnitude and phase

Press Ctrl+C to stop execution and close the GUI.

---

## 🖼️ Plots

- Left plot: Magnitude of cross-correlation
- Right plot: Phase of cross-correlation (in radians)

Both are updated in real-time after each accumulation cycle.

## 🧪 Parameters
Parameter | Description | Default
ACCUMULATIONS | Number of FFT snapshots to average | 1000
MAX_BIN | Use maximum bin of the spectrum (True) or a fixed bin (False) | True
BIN_NUMBER | FFT bin index to analyze if MAX_BIN = False | 51
bitstream_path | Path to your FPGA .fpg file | (edit this value directly in script)
fft_snap_block | Name of the snapshot block in the design | adc_voltage_filtered_snap2_ss
| `fft_snap_block` | Name of the snapshot block in the design   | `adc_voltage_filtered_snap2_ss`     |


