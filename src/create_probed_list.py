import subprocess

def call_httprobe():
    print('Setting up probed_list')
    with open('output.txt', 'a') as output:
        subprocess.call('type cert_list.txt | docker run -i httprobe >> probed_list.txt', shell=True, stdout=output, stderr=output)
        subprocess.call('type extended_cert_list.txt | docker run -i httprobe >> probed_list.txt', shell=True, stdout=output, stderr=output)
    print('Finished setting up probed_list')

if __name__ == "__main__":
    call_httprobe()