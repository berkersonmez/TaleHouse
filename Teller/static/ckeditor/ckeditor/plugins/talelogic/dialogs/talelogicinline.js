/**
 * Created by brkrs_000 on 20.2.2015.
 */
CKEDITOR.dialog.add( 'talelogicinlineDialog', function ( editor ) {
    var ckeditor_talelogic_condition_list = [ [ 'Select a condition...', '-1' ], [ 'Larger than or equal to', '>=' ], [ 'Smaller than or equal to', '<=' ], [ 'Equals', '=' ] ];
    return {
        title: 'Add Conditional Inline Text',
        minWidth: 400,
        minHeight: 200,

        contents: [
            {
                id: 'tab-conj-1',
                label: 'Conjunction Group 1',
                elements: [
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-1-1',
                                items: ckeditor_talelogic_variable_list,
                                'default': '-1',
                                validate: CKEDITOR.dialog.validate.notEqual( "-1", "First variable field cannot be empty." ),
                                setup: function ( widget ) {
                                    if (widget.data.var_1_1 != null)
                                        this.setValue(widget.data.var_1_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_1_1', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_1_1', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-1-1',
                                items: ckeditor_talelogic_condition_list,
                                'default': '-1',
                                validate: CKEDITOR.dialog.validate.notEqual( "-1", "First condition field cannot be empty." ),
                                setup: function ( widget ) {
                                    if (widget.data.logic_1_1 != null)
                                        this.setValue(widget.data.logic_1_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_1_1', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-1-1',
                                validate: function() {
                                    var value = this.getValue();
                                    if ( !value || isNaN(value) || parseFloat(value) != parseInt(value)) {
                                        alert('First value field cannot be empty and should be an integer.' );
                                        return false;
                                    }
                                },
                                setup: function ( widget ) {
                                    if (widget.data.value_1_1 != null)
                                        this.setValue(widget.data.value_1_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_1_1', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-1-2',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_1_2 != null)
                                        this.setValue(widget.data.var_1_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_1_2', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_1_2', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-1-2',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_1_2 != null)
                                        this.setValue(widget.data.logic_1_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_1_2', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-1-2',
                                setup: function ( widget ) {
                                    if (widget.data.value_1_2 != null)
                                        this.setValue(widget.data.value_1_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_1_2', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-1-3',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_1_3 != null)
                                        this.setValue(widget.data.var_1_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_1_3', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_1_3', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-1-3',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_1_3 != null)
                                        this.setValue(widget.data.logic_1_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_1_3', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-1-3',
                                setup: function ( widget ) {
                                    if (widget.data.value_1_3 != null)
                                        this.setValue(widget.data.value_1_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_1_3', this.getValue())
                                }
                            }
                        ]
                    }
                ]
            },
            {
                id: 'tab-conj-2',
                label: 'Conjunction Group 2',
                elements: [
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-2-1',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_2_1 != null)
                                        this.setValue(widget.data.var_2_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_2_1', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_2_1', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-2-1',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_2_1 != null)
                                        this.setValue(widget.data.logic_2_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_2_1', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-2-1',
                                setup: function ( widget ) {
                                    if (widget.data.value_2_1 != null)
                                        this.setValue(widget.data.value_2_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_2_1', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-2-2',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_2_2 != null)
                                        this.setValue(widget.data.var_2_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_2_2', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_2_2', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-2-2',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_2_2 != null)
                                        this.setValue(widget.data.logic_2_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_2_2', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-2-2',
                                setup: function ( widget ) {
                                    if (widget.data.value_2_2 != null)
                                        this.setValue(widget.data.value_2_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_2_2', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-2-3',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_2_3 != null)
                                        this.setValue(widget.data.var_2_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_2_3', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_2_3', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-2-3',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_2_3 != null)
                                        this.setValue(widget.data.logic_2_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_2_3', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-2-3',
                                setup: function ( widget ) {
                                    if (widget.data.value_2_3 != null)
                                        this.setValue(widget.data.value_2_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_2_3', this.getValue())
                                }
                            }
                        ]
                    }
                ]
            },
            {
                id: 'tab-conj-3',
                label: 'Conjunction Group 3',
                elements: [
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-3-1',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_3_1 != null)
                                        this.setValue(widget.data.var_3_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_3_1', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_3_1', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-3-1',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_3_1 != null)
                                        this.setValue(widget.data.logic_3_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_3_1', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-3-1',
                                setup: function ( widget ) {
                                    if (widget.data.value_3_1 != null)
                                        this.setValue(widget.data.value_3_1);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_3_1', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-3-2',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_3_2 != null)
                                        this.setValue(widget.data.var_3_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_3_2', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_3_2', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-3-2',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_3_2 != null)
                                        this.setValue(widget.data.logic_3_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_3_2', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-3-2',
                                setup: function ( widget ) {
                                    if (widget.data.value_3_2 != null)
                                        this.setValue(widget.data.value_3_2);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_3_2', this.getValue())
                                }
                            }
                        ]
                    },
                    {
                        type: 'hbox',
                        widths: [ '40%', '40%', '20%' ],
                        children: [
                            {
                                type: 'select',
                                id: 'var-3-3',
                                items: ckeditor_talelogic_variable_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.var_3_3 != null)
                                        this.setValue(widget.data.var_3_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('var_3_3', this.getValue());
                                    var element = this.getInputElement().$;
                                    var elementDesc = element.options[element.selectedIndex].text;
                                    widget.setData('varDesc_3_3', elementDesc);
                                }
                            },
                            {
                                type: 'select',
                                id: 'logic-3-3',
                                items: ckeditor_talelogic_condition_list,
                                default: '-1',
                                setup: function ( widget ) {
                                    if (widget.data.logic_3_3 != null)
                                        this.setValue(widget.data.logic_3_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('logic_3_3', this.getValue())
                                }
                            },
                            {
                                type: 'text',
                                id: 'value-3-3',
                                setup: function ( widget ) {
                                    if (widget.data.value_3_3 != null)
                                        this.setValue(widget.data.value_3_3);
                                },
                                commit: function ( widget ) {
                                    widget.setData('value_3_3', this.getValue())
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    };
});