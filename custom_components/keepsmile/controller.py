async def connect(self, device: BLEDevice, client: BleakClient | None = None):
        from bleak_retry_connector import establish_connection, BleakClientWithServiceCache

        # Connect client if not provided
        if client is None or not client.is_connected:
            client = await establish_connection(
                BleakClientWithServiceCache,
                device,
                device.name or str(device.address),
                max_attempts=3
            )

        compiler = self.compiler()
        transmitter_fetcher = self.get_transmitter

        # --- FIX: KS03~ uses new commands, but might use the old fff0 Bluetooth service ---
        if device.name and device.name.startswith("KS03~"):
            has_old_protocol = any("fff0" in s.uuid.lower() for s in client.services)
            if has_old_protocol:
                # Keep the NEW compiler, but use the OLD service UUIDs
                compiler = KS03NewCompiler()
                
                def fallback_fetcher(c):
                    return BLETransmitter(c, GattProfile.new("fff0", "fff3", "fff3", "fff3"))
                transmitter_fetcher = fallback_fetcher
        # -------------------------------------------------------------------------

        # Wrap BleakClient in a command transmitter
        transmitter = transmitter_fetcher(client)
        return Connection(compiler, transmitter)