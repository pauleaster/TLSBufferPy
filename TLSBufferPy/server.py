import asyncio
import ssl
import os

class Server:
    def __init__(self, certificate_env_var, private_key_env_var, server_ip, port):
        # Retrieve certificate and private key data from environment variables
        self.certificate_data = os.environ.get(certificate_env_var)
        self.private_key_data = os.environ.get(private_key_env_var)
        
        # Check if the certificate and private key data are provided
        if not self.certificate_data or not self.private_key_data:
            raise ValueError("Certificate or private key data missing.")
        
        # Create a default SSL context for server-side operations
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ctx.load_cert_chain(certfile=None, keyfile=None, 
                                 cadata=self.certificate_data, 
                                 password=None, keydata=self.private_key_data)
        # Set the context to work in server mode
        self.ctx.load_default_certs(ssl.Purpose.CLIENT_AUTH)
        
        # Initialize other attributes
        self.server_ip = server_ip
        self.port = port
        self.server = None
        self.client_reader = None
        self.client_writer = None

    async def startListening(self):
        # Create an asynchronous server coroutine
        self.server = await asyncio.start_server(
            self.acceptConnection, 
            host=self.server_ip, 
            port=self.port, 
            ssl=self.ctx
        )
        print("Server started, listening for connections...")

    async def acceptConnection(self, reader, writer):
        # Store the client reader and writer for future communication
        self.client_reader = reader
        self.client_writer = writer
        print(f"Accepted connection from {writer.get_extra_info('peername')}")

    async def receiveData(self):
        try:
            # Read data from the client
            data = await self.client_reader.read(100)  # reading up to 100 bytes
            message = data.decode()
            print(f"Received message: {message}")
            return message
        except ConnectionResetError:
            print("Connection was closed by the client.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    async def closeConnection(self):
        if self.client_writer:
            self.client_writer.close()
            await self.client_writer.wait_closed()
            print("Connection closed.")
        else:
            print("No active connection to close.")

    async def run(self):
        await self.startListening()
        # Note: In an actual application, you'd typically keep the server running in a loop to handle multiple clients.
        # For simplicity, we're just handling one connection here.
        message = await self.receiveData()
        await self.closeConnection()
        return message