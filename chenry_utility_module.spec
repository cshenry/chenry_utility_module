/*
A KBase module: chenry_utility_module
*/

module chenry_utility_module {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;
	
    funcdef activate_callback_server(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
