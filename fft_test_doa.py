import casperfpga
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Choose appropriate backend for your GUI
import matplotlib.pyplot as plt
import math
import signal
import sys

ACCUMULATIONS = 1000

# Handle graceful exit
def signal_handler(sig, frame):
    print('\n[INFO] Exiting...')
    plt.close('all')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initialize FPGA connection
fpga = casperfpga.CasperFpga('10.0.0.19')

# first fft snap: /home/vboxuser/Work/doa_freq_corr_adc/outputs/doa_freq_corr_adc_2025-04-15_0948.fpg
# second fft snap: /home/vboxuser/Work/doa_freq_corr_adc/outputs/doa_freq_corr_adc_2025-04-15_1131.fpg
# both fft snaps are readable: /home/vboxuser/Work/doa_freq_corr_adc/outputs/doa_freq_corr_adc_2025-04-15_1144.fpg
# both fft outputs go to the same snapshot block: /home/vboxuser/Work/doa_freq_corr_adc/outputs/doa_freq_corr_adc_2025-04-16_1006.fpg
bitstream_path = '/home/vboxuser/Work/doa_freq_corr_adc/outputs/doa_freq_corr_adc_2025-04-16_1006.fpg'
fpga.upload_to_ram_and_program(bitstream_path)

print(f"[INFO] Bitstream loaded: {bitstream_path}")
print(f"[INFO] Number of accumulations: {ACCUMULATIONS}")

# Setup plots
fig, ax = plt.subplots(1, 2, figsize=(18, 6))  # 1x2 subplot
ax_mag_re = ax[0]    # Left subplot
ax_mag_im = ax[1]    # Right subplot

acc_counter = 0

# Main loop
while True:
    # Arm snapshot
    fpga.snapshots.adc_voltage_filtered_snap2_ss.arm()

    # Read snapshot
    snap2_fft_data = fpga.snapshots.adc_voltage_filtered_snap2_ss.read(arm=False)['data']

    # Store real and imaginary fft data of each channel in numpy arrays
    fft_re_1 = np.array(snap2_fft_data['fft_op_re_1'])
    fft_im_1 = np.array(snap2_fft_data['fft_op_im_1'])

    fft_re_2 = np.array(snap2_fft_data['fft_op_re_2'])
    fft_im_2 = np.array(snap2_fft_data['fft_op_im_2'])

    # Form complex spectra for each channel
    fft_cplx_1 = fft_re_1 + 1j * fft_im_1
    fft_cplx_2 = fft_re_2 + 1j * fft_im_2

    # Print FFT length once
    fft_len = len(fft_cplx_1)
    print(f"\n[INFO] FFT Length: {fft_len}")

    # Take only the first half of each spectrum
    fft_cplx_1 = fft_cplx_1[:fft_len // 2]
    fft_cplx_2 = fft_cplx_2[:fft_len // 2]

    # Calculate the cross-correlation
    cross_corr_fft = fft_cplx_1 * np.conj(fft_cplx_2)

    # Initialize buffer to store cross-correlation accumulations
    if acc_counter == 0:
        cross_corr_fft_buffer = np.zeros_like(cross_corr_fft)

    # Accumulate cross-correlation buffer
    cross_corr_fft_buffer += cross_corr_fft

    # -----------------------------------------------------------------------------
    # Calculate phase diff through looking at max bin for each FFT (for comparison) - START
    # -----------------------------------------------------------------------------
    fft_1_mag = np.abs(fft_cplx_1)
    fft_2_mag = np.abs(fft_cplx_2)
    fft_1_mag_max_index = np.argmax(fft_1_mag)
    fft_2_mag_max_index = np.argmax(fft_2_mag)
    fft_1_phase_at_max_index = np.angle(fft_cplx_1[fft_1_mag_max_index])
    fft_2_phase_at_max_index = np.angle(fft_cplx_2[fft_2_mag_max_index])
    fft_phase_diff = np.degrees(fft_1_phase_at_max_index - fft_2_phase_at_max_index)

    print("[DEBUG] Max Bin Phase Comparison:")
    print(f"  FFT_1 Max Index: {fft_1_mag_max_index}, Phase: {np.degrees(fft_1_phase_at_max_index):.2f}°")
    print(f"  FFT_2 Max Index: {fft_2_mag_max_index}, Phase: {np.degrees(fft_2_phase_at_max_index):.2f}°")
    print(f"  Phase Difference (Direct Subtraction): {fft_phase_diff:.2f}°")
    # -----------------------------------------------------------------------------
    # Calculate phase diff through looking at max bin for each FFT (for comparison) - END
    # -----------------------------------------------------------------------------

    # Go in here after the specified amount of accumulations have been reached
    if acc_counter >= ACCUMULATIONS:

        # -------------------------------------------------------------------------------------------------------------------------
        # Calculate phase diff through looking at the phase of the cross-correlation where it has a peak in it's magnitude spectrum - START
        # -------------------------------------------------------------------------------------------------------------------------

        # Calculate the average of the cross-correlation buffer (cc = cross-correlation)
        cc_average = cross_corr_fft_buffer / ACCUMULATIONS

        # Calculate the magnitude of the average of the cc buffer
        cc_average_mag = np.abs(cc_average)

        # Calculate max magnitude index of cc_average_mag
        cc_average_mag_max_index = np.argmax(cc_average_mag)

        # Calculate the phase diff by looking at the phase at max magnitude
        cc_average_phase_at_max_index = np.angle(cc_average[cc_average_mag_max_index])

        # Calculate the phase shift in degrees
        cc_phase_diff = np.degrees(cc_average_phase_at_max_index)

        print("\n[RESULT] Cross-Correlation Phase Analysis:")
        print(f"  Max Bin Index (Cross-Corr): {cc_average_mag_max_index}")
        print(f"  Phase Difference (Cross-Corr): {cc_phase_diff:.2f}°")
        print(f"  Number of Accumulations: {ACCUMULATIONS}")

        # -------------------------------------------------------------------------------------------------------------------------
        # Calculate phase diff through looking at the phase of the cross-correlation where it has a peak in it's magnitude spectrum - END
        # -------------------------------------------------------------------------------------------------------------------------

        # Plot mag of cross-correlation
        ax_mag_re.cla()
        ax_mag_re.set_title("Magnitude of cross-correlation")
        ax_mag_re.set_xlabel("Sample Index (Bin Number)")
        ax_mag_re.set_ylabel("Amplitude (not dB)")
        ax_mag_re.plot(cc_average_mag)

        # Plot phase of cross-correlation
        ax_mag_im.cla()
        ax_mag_im.set_title("Phase of cross-correlation")
        ax_mag_im.set_xlabel("Sample Index (Bin Number)")
        ax_mag_im.set_ylabel("Amplitude (radians)")
        ax_mag_im.plot(np.angle(cc_average))

        plt.pause(0.1)

        # Reset acc_counter to start a new accumulation cycle
        acc_counter = 0

    else:
        acc_counter += 1
