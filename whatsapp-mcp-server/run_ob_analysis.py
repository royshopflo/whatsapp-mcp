#!/usr/bin/env python3
"""
Script to run the analysis of WhatsApp OB groups and generate a report.
"""

import sys
import os
import argparse
from datetime import datetime
from analyze_ob_groups_5days import (
    analyze_ob_groups,
    generate_report,
    save_report_to_file,
    print_report,
    DAYS_TO_ANALYZE,
    OB_GROUP_SEARCH_TERM,
    TEAM_NUMBERS_FILE
)

def main():
    """Main function to run the analysis and generate a report."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze WhatsApp (OB) groups and classify merchant sentiment')
    
    parser.add_argument('--days', type=int, default=DAYS_TO_ANALYZE,
                        help=f'Number of days to analyze (default: {DAYS_TO_ANALYZE})')
    
    parser.add_argument('--show-team-numbers', action='store_true',
                        help='Show the path to the team numbers file and exit')
    
    parser.add_argument('--report-file', type=str, default=None,
                        help='Custom filename for the report (default: auto-generated with timestamp)')
    
    args = parser.parse_args()
    
    # If the user just wants to know where the team numbers file is
    if args.show_team_numbers:
        print(f"Shopflo team numbers file location: {TEAM_NUMBERS_FILE}")
        print("You can edit this file to add your team phone numbers for better message classification.")
        sys.exit(0)
    
    # Display banner
    print("\n" + "="*60)
    print("                WHATSAPP OB GROUPS ANALYSIS                ")
    print("="*60 + "\n")
    
    print(f"Starting analysis of WhatsApp groups with '{OB_GROUP_SEARCH_TERM}' in their name...")
    print(f"Analyzing messages from the last {args.days} days.")
    print("This may take some time, please wait...\n")
    
    # Run the analysis
    results = analyze_ob_groups()
    
    # Print a summary to the console
    print_report(results)
    
    # Generate a more detailed markdown report
    report = generate_report(results)
    
    # Save the report with a timestamp in the filename
    if args.report_file:
        report_filename = args.report_file
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ob_groups_report_{timestamp}.md"
    
    report_path = save_report_to_file(report, report_filename)
    
    print(f"\nDetailed analysis report saved to: {report_path}")
    print("You can open this file to see the full analysis results.")
    
    print("\nTIP: To add Shopflo team phone numbers for better classification of messages,")
    print(f"edit the file at: {TEAM_NUMBERS_FILE}")
    print("These numbers help distinguish between team members and merchants in chats.")

if __name__ == "__main__":
    main() 