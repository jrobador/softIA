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
          title: Text('Todavía no has subido archivos'),
          content: Text('Estas seguro que querés continuar sin subir archivos?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text('Cancelar'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: Text('Proceder sin archivos'),
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
        SnackBar(content: Text('Subiendo archivos y procesando...')),
      );

      await apiService.uploadPdfs(
        useCase: _useCase,
        pdfFiles: _selectedFiles,
      );

      Chatbot newChatbot = Chatbot(
        id: Uuid().v4(),
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
      return Text('No has subido archivos PDF aún');
    }
    return Column(
      children: _selectedFiles
          .map((file) => ListTile(
                leading: Icon(Icons.picture_as_pdf, color: Colors.red),
                title: Text(file.path.split('/').last),
              ))
          .toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Crear tu propio asistente virtual personalizado'),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            TextFormField(
                              decoration: InputDecoration(labelText: '¿Con qué nombre querés llamar a tu asistente virtual?'),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Por favor ingresa un nombre para tu asistente virtual';
                                }
                                return null;
                              },
                              onSaved: (value) => _name = value!,
                            ),
                            TextFormField(
                              decoration: InputDecoration(labelText: '¿Para qué querés tu asistente virtual?'),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Por favor, ingresá para qué querés tu asistente virtual';
                                }
                                return null;
                              },
                              onSaved: (value) => _useCase = value!,
                            ),
                            SizedBox(height: 20),
                            DropdownButtonFormField<String>(
                              value: _retrainingFrequency,
                              decoration: InputDecoration(labelText: '¿Cada cuanto querés reentrenar tu asistente virtual?'),
                              items: ['Diario', 'Semanal', 'Personalizado', 'No reentrenar']
                                  .map((option) => DropdownMenuItem(
                                        value: option,
                                        child: Text(option),
                                      ))
                                  .toList(),
                              onChanged: (value) {
                                setState(() {
                                  _retrainingFrequency = value!;
                                });
                              },
                            ),
                            SizedBox(height: 20),
                            SwitchListTile(
                              title: Row(
                                children: [
                                  Text('Procesamiento '),
                                  Text(
                                    _isLocal ? 'local' : 'en la nube',
                                    style: TextStyle(fontWeight: FontWeight.bold),
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
                            ElevatedButton.icon(
                              onPressed: _pickFiles,
                              icon: Icon(Icons.attach_file),
                              label: Text('Subí tus archivos PDF'),
                            ),
                            SizedBox(height: 10),
                            _buildFileList(),
                            SizedBox(height: 30),
                            ElevatedButton(
                              onPressed: _submit,
                              child: Text('Entrenar asistente virtual'),
                              style: ElevatedButton.styleFrom(
                                minimumSize: Size(double.infinity, 50),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  Padding(
                    padding: EdgeInsets.only(top: 16.0),
                    child: ElevatedButton.icon(
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => QuickStartGuide(
                            onClose: () => Navigator.of(context).pop(),
                          ),
                        );
                      },
                      icon: Icon(Icons.lightbulb_outline),
                      label: Text('Guía rápida de inicio'),
                      style: ElevatedButton.styleFrom(
                        minimumSize: Size(double.infinity, 50),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}