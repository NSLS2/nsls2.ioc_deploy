# ADProsilica Role

This role configures EPICS IOCs for Prosilica/Allied Vision GigE cameras using the ADProsilica driver.

## Description

The ADProsilica role sets up IOCs for Prosilica cameras with the following features:
- Camera configuration and connection
- Standard array plugin for image data
- Common plugins for data processing
- Autosave configuration for persistent settings

## Required Environment Variables

- `PREFIX`: EPICS PV prefix for the camera
- `ENGINEER`: Name of the engineer responsible for the IOC
- `XSIZE`: Image width in pixels
- `YSIZE`: Image height in pixels
- `CAMERA_ID`: Camera IP address or hostname

## Usage

See `example.yml` for a complete configuration example.
