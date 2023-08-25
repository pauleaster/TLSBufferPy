import asyncio
import ssl
import os


class Client:
    def __init__(self, certificate_env_var, private_key_env_var, server_ip, port):

        self.server_ip = server_ip
        self.port = port
        self.reader = None
        self.writer = None
        # Retrieve certificate and private key data from environment variables
        self.certificate_data = os.environ.get(certificate_env_var)
        self.private_key_data = os.environ.get(private_key_env_var)

        # Check if the certificate and private key data are provided
        if not self.certificate_data or not self.private_key_data:
            raise ValueError("Certificate or private key data missing.")

        # Create a default SSL context
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        # Enforce TLS v1.3
        self.ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        self.ctx.maximum_version = ssl.TLSVersion.TLSv1_3

        # Load the client certificate and private key into the SSL context
        self.ctx.load_cert_chain(
            certfile=None,
            keyfile=None,
            cadata=self.certificate_data,
            password=None,
            keydata=self.private_key_data,
        )

        # Initialize other attributes
        self.connected = False
        self.server_ip = None
        self.port = None

    async def connect(self):
        # Create an SSL connection to the server
        self.reader, self.writer = await asyncio.open_connection(
            host=self.server_ip, port=self.port, ssl=self.ctx
        )
        self.connected = True
        print("Connected to the server")

    async def send(self, message):
        if not self.connected:
            print("Not connected. Cannot send message.")
            return

        self.writer.write(message.encode())
        await self.writer.drain()
        print("Message sent")

    async def disconnect(self):
        if not self.connected:
            print("Not connected.")
            return

        self.writer.close()
        await self.writer.wait_closed()
        self.connected = False
        print("Disconnected from the server")

    def check_certificate(self):
        # Check certificate verification status
        if self.ctx.verify_mode == ssl.CERT_REQUIRED:
            print("Certificate verification is enabled")
        else:
            print("Certificate verification is disabled")

        # Display part of the certificate for demonstration purposes
        print("Certificate: \n", self.certificate_data[:100], "...")

    def check_private_key(self):
        # For simplicity, we're just verifying the presence of the private key data
        if self.private_key_data:
            print("Private key is available")
            # Display part of the private key for demonstration purposes
            print("Private key: \n", self.private_key_data[:100], "...")
        else:
            print("Private key is not available")
