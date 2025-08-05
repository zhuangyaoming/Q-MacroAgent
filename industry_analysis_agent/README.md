# Industry Analysis Agent

This project is designed to analyze multiple company reports in JSON format and generate comprehensive industry analysis reports. The main component of the project is the `IndustryAgent` class, which is responsible for loading company reports, extracting relevant industry data, and creating analysis reports.

## Project Structure

- `src/agent.py`: Defines the `IndustryAgent` class, which includes methods for loading reports, generating industry analysis, extracting industry data, and creating analysis reports.
  
- `src/deepseek/api.py`: Contains functions for interacting with the Deep Seek API, including `call_deep_seek_api`, which sends industry data and retrieves analysis results.
  
- `src/utils/report_reader.py`: Includes utility functions for reading company reports, such as `read_reports`, which reads and parses JSON formatted company analysis reports from specified paths.
  
- `src/types.py`: Defines types and data structures used in the project, including `IndustryAnalysisReport` and `CompanyReport`.

- `requirements.txt`: Lists the required Python dependencies for the project, which can be installed using `pip`.

## Usage

1. Ensure you have Python installed on your machine.
2. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```
3. Prepare your JSON formatted company analysis reports and specify their paths.
4. Create an instance of the `IndustryAgent` class and call the `generate_industry_analysis` method to obtain the analysis report.

## Contributing

Contributions to the project are welcome. Please feel free to submit issues or pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License.