import subprocess


def convert_to_pdf(input_file, output_file, libreoffice_exec):
    command = [libreoffice_exec, "--headless", "--convert-to", "pdf", "--outdir", output_file, input_file]

    subprocess.run(command)

