"""

Remote control of Red Pitaya using SCPI.
Wraps the existing red pitaya scipi control library
to make it more user friendly



Author: Will Thompson, May 2017
"""

# Check if we are running in a Jupyter Notebook
# If so, import stuff for prettier displays
try:
    _cfg = get_ipython()
    _running_in_jupyter = True
    import IPython.display
except NameError:
    _running_in_jupyter = False

class ConnectRedPitaya(object):
    
    def __init__(self, address="localhost", port=5000, verbose=True):
        
        self._address = address
        self.verbose = verbose
        try:
            self._scpi = _scpi(self._address, timeout=6, port=port)
        except Exception as err:
            
            if _running_in_jupyter:
                IPython.display.display(IPython.display.HTML("""
                    <p style='color:darkred'>Error connecting to RedPitaya at "{0}:{1}"</p>
                    <p>Visit <a target="_blank" href="http://{0}/scpi_manager/">http://{0}/scpi_manager/</a> to start the SCPI server.</p>
                    <p>If you can't visit that website, check you have the correct address by looking at the sticker:</p>
                    <img width=250 src="http://redpitaya.readthedocs.io/en/latest/_images/Screen-Shot-2016-08-17-at-09.50.31-503x600.png"</p>
                """.format(address, port)))
            else:
                print("Error connecting to RedPitaya at \"{}:{}\"".format(address, port))
                print("Visit http://{}/scpi_manager/ to start the SCPI server.".format(address))
                print("If you can't visit that website, check you have the correct address by looking at the sticker.")            
                print()
            
            raise
        
        self("*RST")
        self("*CLS")
        self.idn = self("*IDN?")
        print("Connected to", self.idn)
        
    def flush(self):
        """\
        Flush the receive buffer and ignore its contents
        """
        self._scpi._socket.settimeout(0.1)
        chunksize = 4096
        chunk = ""
        while 1:
            try:
                chunk = self._scpi._socket.recv(chunksize).decode('utf-8') # Receive chunk size of 2^n preferably
            except _socket.timeout:
                self._scpi._socket.settimeout(6)
                return 
            if len(chunk) == 0:
                self._scpi._socket.settimeout(6)
                return
            
    def __call__(self, command, *args, dtype=str, verbose=None):
        if verbose is None:
            verbose = self.verbose
        command = command.strip()
        command = str(command)+" "+(" ".join(str(a) for a in args))
        self._scpi.tx_txt(command)
        if verbose:
            print(self._address, '<--', command)
        output = None
        
        error_check = self._scpi.rx_err()
        if error_check:
            # Now check for an error
            errno = -1
            message = ''
            messages = []
            invalid = False
            while errno != 0:
                self._scpi.tx_txt("SYST:ERR?")
                errno, message = self._scpi.rx_txt().split(",")
                errno = float(errno.split('!')[-1])
                message = bytes(message, "ascii")[1:-1].decode('unicode_escape')
                if errno != 0:
                    if 'undefined header' in message.lower():
                        message += ' (invalid command)'
                        invalid = True
                    messages.append(message)
                    print(self._address, '-->', "An error occured on the Red Pitaya:", message)
                                        
            if invalid and _running_in_jupyter:
                IPython.display.display(IPython.display.HTML("""
                    <p><span style='color:darkred'>The command "<span style='color:black;font-weight:bold'>{}</span>" is invalid.</span> Click <a href="http://redpitaya.readthedocs.io/en/latest/doc/appsFeatures/remoteControl/remoteControl.html#list-of-supported-scpi-commands" target="_blank">here</a> for a list of valid commands.
                 """.format(command)))
                    
            raise Exception("An error occured on the Red Pitaya: "+(', '.join(messages)))
            
            self._scpi.tx_txt("SYST:ERR?")
            print('check error')
            errors, message = self._scpi.rx_txt().split(",")   
            print(errors, message)
        
        if '?' in command:
            output = self._scpi.rx_txt()
            if verbose:
                print(self._address, '-->', output[:76], '...' if len(output) > 80 else '')
                
            # Convert output as requested
            try:
                if dtype is not str:
                    output = dtype(output)
            except ValueError:
                print("Data type conversion error: you specified dtype={}, but the Red Pitaya responded with \"{}\"".format(str(dtype), output))
                raise

        
        return output

def convert_scpi_list_to_array(string_input):
    import numpy as np
    
    # Ensure we are provided with a long enough string
    assert len(string_input) > 2, "Invalid input to convert_scpi_list_to_array"
    
    if "WAIT" in string_input:
        raise ValueError("Cannot convert string to numpy array:"+string_input)
    
    # Remove first and last characters
    string_input_without_first_and_last_characters = string_input[1:-1]
    
    # Convert long string with commas in it to a list of strings containing numbers
    list_of_number_strings = string_input_without_first_and_last_characters.split(',')
    
    # Loop through the list of strings containing numbers and convert each to a value
    list_of_numbers = []
    for string in list_of_number_strings:
        try:
            number = float(string) # Convert to number
            list_of_numbers.append(number) # Add to list
        except Exception as err:
            print("Error parsing:")
            print(string)
            print("From the response:")
            print(string_input)
            raise

    
    # Now convert list to a numpy array of floats
    array_of_numbers = np.array(list_of_numbers)
    
    return array_of_numbers

import socket as _socket

# __author__ = "Luka Golinar, Iztok Jeras"
# __copyright__ = "Copyright 2015, Red Pitaya"

class _scpi (object):
    """SCPI class used to access Red Pitaya over an IP network."""
    delimiter = '\r\n'

    def __init__(self, host, timeout=None, port=5000):
        """Initialize object and open IP connection.
        Host IP should be a string in parentheses, like '192.168.1.100'.
        """
        self.host    = host
        self.port    = port
        self.timeout = timeout
        self.msg = ''

        self._socket = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

        if timeout is not None:
            self._socket.settimeout(timeout)

        self._socket.connect((host, port))

    def rx_txt(self, chunksize = 4096):
        """Receive text string and return it after removing the delimiter."""
        chunk = ''
        if self.delimiter not in self.msg:
            while len(chunk)==0 or self.delimiter not in chunk:
                chunk = self._socket.recv(chunksize + len(self.delimiter)).decode('utf-8') # Receive chunk size of 2^n preferably
                self.msg += chunk
        parts = self.msg.split(self.delimiter)
        self.msg = self.delimiter.join(parts[1:])
        return parts[0]
                

    def rx_err(self, chunksize = 4096):
        """Receive text string and return it after removing the delimiter."""
        temp_timeout = self._socket.gettimeout()
        self._socket.settimeout(0.1)
        while 1:
            try:
                chunk = self._socket.recv(chunksize + len('!')).decode('utf-8') # Receive chunk size of 2^n preferably
            except _socket.timeout:
                self._socket.settimeout(temp_timeout)
                return False
            # If we get an error message, exit and set the buffer to anything following it
            if (len(chunk) and '!' in chunk):
                self.msg = chunk.split('!')[-1]
                self._socket.settimeout(temp_timeout)
                return True
            # Otherwise, if we saw the end of a message there's no error; add it to the buffer and exit
            elif (len(chunk) and self.delimiter in chunk):  
                self.msg += chunk
                self._socket.settimeout(temp_timeout)
                return False
            # Otherwise, add to the buffer
            else:
                self.msg += chunk
            


    def rx_arb(self):
        numOfBytes = 0
        """ Recieve binary data from scpi server"""
        str=''
        while (len(str) != 1):
            str = (self._socket.recv(1))
        if not (str == '#'):
            return False
        str=''
        while (len(str) != 1):
            str = (self._socket.recv(1))
        numOfNumBytes = int(str)
        if not (numOfNumBytes > 0):
            return False
        str=''
        while (len(str) != numOfNumBytes):
            str += (self._socket.recv(1))
        numOfBytes = int(str)
        str=''
        while (len(str) != numOfBytes):
            str += (self._socket.recv(1))
        return str

    def tx_txt(self, msg):
        """Send text string ending and append delimiter."""
        return self._socket.send((msg + self.delimiter).encode('utf-8'))

    def close(self):
        """Close IP connection."""
        self.__del__()

    def __del__(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None