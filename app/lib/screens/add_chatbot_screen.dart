import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:uuid/uuid.dart';
import '../providers/chatbot_provider.dart';
import '../models/chatbot.dart';
import '../services/api_service.dart';
import './quick_start_guide.dart';

class AddChatbotScreen extends StatefulWidget {
  @override
  _AddChatbotScreenState createState() => _AddChatbotScreenState();
}

class _AddChatbotScreenState extends State<AddChatbotScreen> {
  final _formKey = GlobalKey<FormState>();
  String _name = '';
  String _useCase = '';
  String _retrainingFrequency = 'Diario';
  List<File> _selectedFiles = [];
  bool _isLoading = false;
  bool _isLocal = true;

  final ApiService apiService = ApiService(baseUrl: 'http://127.0.0.1:8000');

  Future<void> _pickFiles() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      allowMultiple: true,
    );

    if (result != null) {
      setState(() {
        _selectedFiles = result.paths.map((path) => File(path!)).toList();
      });
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedFiles.isEmpty) {
      bool proceed = await showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Todavía no has subido archivos'),
          content: const Text('Estas seguro que querés continuar sin subir archivos?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Proceder sin archivos'),
            ),
          ],
        ),
      );
      if (!proceed) return;
    }

    for (var file in _selectedFiles) {
      if (!(await file.exists())) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('El archivo no existe: ${file.path}')),
        );
        return;
      }
    }

    _formKey.currentState!.save();

    setState(() {
      _isLoading = true;
    });

    try {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Subiendo archivos y procesando...')),
      );

      await apiService.uploadPdfs(
        useCase: _useCase,
        pdfFiles: _selectedFiles,
      );

      Chatbot newChatbot = Chatbot(
        id: const Uuid().v4(),
        name: _name,
        useCase: _useCase,
        filePaths: _selectedFiles.map((file) => file.path).toList(),
        isLocal: _isLocal,
      );

      Provider.of<ChatbotProvider>(context, listen: false).addChatbot(newChatbot);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Asistente virtual "${_name}" creado exitosamente')),
      );

      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildFileList() {
    if (_selectedFiles.isEmpty) {
      return const Text('No has subido archivos PDF aún');
    }
    return Column(
      children: _selectedFiles
          .map((file) => ListTile(
                leading: const Icon(Icons.picture_as_pdf, color: Colors.red),
                title: Text(file.path.split('/').last),
              ))
          .toList(),
    );
  }

  Widget _buildResponsiveButton({
    required VoidCallback onPressed,
    required Widget child,
    bool isIcon = false,
  }) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth > 600;
        final buttonWidth = isDesktop ? 400.0 : double.infinity;
        
        return Center(
          child: SizedBox(
            width: buttonWidth,
            child: ElevatedButton(
              onPressed: onPressed,
              style: ElevatedButton.styleFrom(
                minimumSize: Size(buttonWidth, isDesktop ? 60 : 50),
                padding: EdgeInsets.symmetric(
                  horizontal: isDesktop ? 32 : 16,
                  vertical: isDesktop ? 16 : 12,
                ),
              ),
              child: child,
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Crear tu propio asistente virtual personalizado'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // ... los TextFormFields y DropdownButtonFormField permanecen igual ...
                            
                            const SizedBox(height: 20),
                            
                            Center(  // Centramos el SwitchListTile
                              child: ConstrainedBox(
                                constraints: const BoxConstraints(maxWidth: 400),
                                child: SwitchListTile(
                                  title: Row(
                                    children: [
                                      const Text('Procesamiento '),
                                      Text(
                                        _isLocal ? 'local' : 'en la nube',
                                        style: const TextStyle(fontWeight: FontWeight.bold),
                                      ),
                                    ],
                                  ),
                                  value: _isLocal,
                                  onChanged: (value) {
                                    setState(() {
                                      _isLocal = value;
                                    });
                                  },
                                ),
                              ),
                            ),
                            
                            const SizedBox(height: 20),
                            
                            _buildResponsiveButton(
                              onPressed: _pickFiles,
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.attach_file),
                                  SizedBox(width: 8),
                                  Text('Subí tus archivos PDF'),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 10),
                            _buildFileList(),
                            const SizedBox(height: 30),
                            
                            _buildResponsiveButton(
                              onPressed: _submit,
                              child: const Text('Entrenar asistente virtual'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  
                  Padding(
                    padding: const EdgeInsets.only(top: 16.0),
                    child: _buildResponsiveButton(
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => QuickStartGuide(
                            onClose: () => Navigator.of(context).pop(),
                          ),
                        );
                      },
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.lightbulb_outline),
                          SizedBox(width: 8),
                          Text('Guía rápida de inicio'),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}