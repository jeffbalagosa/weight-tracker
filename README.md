# Weight-Tracker Application

## Overview

**Weight-Tracker** is a simple command-line application that helps users track their daily weigh-ins and monitor their progress over time. It stores weight entries in a local SQLite database and provides functionality to view the last 10 entries, calculate the moving average, and update weigh-ins for the current day or a specific date.

GitHub Repository: [Weight-Tracker](https://github.com/jeffbalagosa/weight-tracker)

## Features

- Track daily weigh-ins with the ability to adjust entries.
- View the last 10 weigh-ins along with weight differences.
- Compute a moving average of the last 10 entries.
- Supports adding weigh-ins for specific dates.
- Data is stored locally in a SQLite database for easy management.

## Requirements

To run this app on a Windows machine, ensure you have:

- Python 3.x installed
- SQLite installed (if not already included with Python)

## Setup

1. Clone the repository from GitHub:
   ```
   git clone https://github.com/jeffbalagosa/weight-tracker.git
   cd weight-tracker
   ```

2. Install necessary packages (no additional external libraries required for this app).

3. Run the application using Python:
   ```
   python main.py
   ```

## Usage

When you run the application, you will see the following options:

### Main Menu

- **/w**: Enter or adjust today's weigh-in.
- **/a**: Enter or adjust a weigh-in for a different date.
- **Ctrl + C**: Exit the application.

### Adding or Adjusting Today's Weigh-In

To add or adjust today's weight:
1. Type `/w` and press Enter.
2. You will be prompted to enter today's weight. Enter the value in pounds (numeric format).

### Adding or Adjusting a Previous Date's Weigh-In

To enter or adjust a previous date's weight:
1. Type `/a` and press Enter.
2. Enter the date and weight in the format `YYYY-MM-DD, Weight`, e.g., `2024-09-01, 180.5`.

### Viewing Last 10 Entries

The app will display the last 10 weigh-ins upon starting and after each new weigh-in is recorded. For each weigh-in, the app will show:

- **Date**: The date of the weigh-in.
- **Weight**: The weight recorded on that day.
- **Difference**: The change in weight compared to the previous entry.

It also displays the **Moving Average** of the last 10 weigh-ins.

## Database

The app stores all weigh-ins in a local SQLite database named `weight_tracker.db`. This file is created automatically in the current working directory if it does not exist.

## License

MIT License

Copyright (c) 2024 Jeff Balagosa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software") to deal
in the software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the software, and to permit persons to whom the software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the software.

THE SOFTWARE IS PROVIDED "AS IS"WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
