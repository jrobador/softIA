// lib/services/api_service.dart

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;

  ApiService({required this.baseUrl});

  // Endpoint to upload PDFs and generate dataset
  Future<Map<String, dynamic>> uploadPdfs({
    required String useCase,
    required List<File> pdfFiles,
  }) async {
    var uri = Uri.parse('$baseUrl/finetuning-rag/upload-pdfs');
    var request = http.MultipartRequest('POST', uri);

    // Add the use_case as a form field
    request.fields['use_case'] = useCase;

    // Debug print to verify files are being added
    print('Adding ${pdfFiles.length} files to request');
    
    // Add files explicitly with the correct field name
    for (int i = 0; i < pdfFiles.length; i++) {
      final file = pdfFiles[i];
      final filename = file.path.split('/').last;
      print('Adding file: $filename');
      
      request.files.add(await http.MultipartFile.fromPath(
        'files', // This must match EXACTLY with what FastAPI expects
        file.path,
      ));
    }

    // Print request fields and files for debugging
    print('Request fields: ${request.fields}');
    print('Request files count: ${request.files.length}');
    
    try {
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to upload PDFs: ${response.body}');
      }
    } catch (e) {
      print('Exception during upload: $e');
      throw Exception('Error during upload: $e');
    }
  }

  // Endpoint to list chatbots (if managed via backend)
  // Implement additional API methods as needed
}
