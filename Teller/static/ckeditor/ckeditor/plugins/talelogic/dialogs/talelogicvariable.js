/**
 * Created by brkrs_000 on 20.2.2015.
 */
CKEDITOR.dialog.add( 'talelogicvariableDialog', function ( editor ) {
    return {
        title: 'Show Variable Value in Tale',
        minWidth: 400,
        minHeight: 200,

        contents: [
            {
                id: 'tab-select-variable',
                label: 'Select Variable',
                elements: [
                    {
                        type: 'select',
                        id: 'variable',
                        items: ckeditor_talelogic_variable_list,
                        'default': '-1',
                        label: 'Variable to show the value of',
                        validate: CKEDITOR.dialog.validate.notEqual( "-1", "Variable field cannot be empty." ),
                        setup: function ( widget ) {
                            if (widget.data.variableId != null)
                                this.setValue(widget.data.variableId);
                        },
                        commit: function ( widget ) {
                            widget.setData('variableId', this.getValue());
                            var element = this.getInputElement().$;
                            var elementDesc = element.options[element.selectedIndex].text;
                            widget.setData('variableName', elementDesc);
                        }
                    }
                ]
            }
        ]
    };
});