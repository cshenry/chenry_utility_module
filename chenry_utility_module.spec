/*
A KBase module: chenry_utility_module
*/

module chenry_utility_module {
	
    funcdef activate_callback_server(mapping<string,UnspecifiedObject> params) returns (mapping<string,UnspecifiedObject> output) authentication required;
    
    funcdef run_command(mapping<string,UnspecifiedObject> params) returns (mapping<string,UnspecifiedObject> output) authentication required;

};
