/**
 * Created by brkrs_000 on 20.2.2015.
 */
CKEDITOR.dtd.$editable.span = 1;
CKEDITOR.dtd.$removeEmpty['span'] = false;
CKEDITOR.plugins.add( 'talelogic', {
    requires: 'widget',
    icons: 'talelogic,talelogicinline,talelogicvariable',
    init: function( editor ) {
        CKEDITOR.dialog.add( 'talelogicDialog', this.path + 'dialogs/talelogic.js' );
        CKEDITOR.dialog.add( 'talelogicinlineDialog', this.path + 'dialogs/talelogicinline.js' );
        CKEDITOR.dialog.add( 'talelogicvariableDialog', this.path + 'dialogs/talelogicvariable.js' );
        editor.widgets.add( 'TaleLogic', {
            button: 'Add Conditional Paragraph',

            dialog: 'talelogicDialog',

            template: '<div class="talelogic-outer" data-talelogic="LOGIC_GOES_HERE">' +
                '<div class="talelogic-if"><p class="talelogic-if-condition">LOGIC GOES HERE...</p><div class="talelogic-if-text"><p></p></div></div>' +
                '<div class="talelogic-else"><p class="talelogic-else-condition">else:</p><div class="talelogic-else-text"><p></p></div></div>',

            editables: {
                ifText: {
                    selector: '.talelogic-if-text'
                },
                elseText: {
                    selector: '.talelogic-else-text'
                }
            },

            allowedContent: 'div(!talelogic-outer)[!data-talelogic]; div(!talelogic-if); div(!talelogic-else); p(!talelogic-if-condition); ' +
                'div(!talelogic-if-text); p(!talelogic-else-condition); div(!talelogic-else-text)',

            requiredContent: 'div(talelogic-outer)',

            upcast: function( element ) {
                return element.name == 'div' && element.hasClass( 'talelogic-outer' );
            },

            data: function() {
                var logEx = '';
                var logExPrev = '';

                for (var i = 1; i < 4; i++)
                {
                    for (var j = 1; j < 4; j++)
                    {
                        var tVar = this.data['var_' + i + '_' + j];
                        if (tVar == '-1' || isNaN(tVar)) break;
                        var tVarDesc = this.data['varDesc_' + i + '_' + j];

                        var tCon = this.data['logic_' + i + '_' + j];
                        if (tCon == '-1') break;

                        var tVal = this.data['value_' + i + '_' + j];
                        if (!tVal || tVal == '' || isNaN(tVal)) break;

                        if (j == 1) {
                            if (i != 1) {
                                logEx = logEx + ' or ';
                                logExPrev = logExPrev + ' or ';
                            }
                            logEx = logEx + '(';
                            logExPrev = logExPrev + '(';
                        }

                        if (j != 1) {
                            logEx = logEx + ' and ';
                            logExPrev = logExPrev + ' and ';
                        }
                        logEx = logEx + "{'" + tVar + "'" + ' ' + tCon + ' ' + tVal + "}";
                        logExPrev = logExPrev + '"' + tVarDesc + '"' + ' ' + tCon + ' ' + tVal;
                    }
                    if (logEx.substr(logEx.length - 1) != ')') {
                        logEx = logEx + ')';
                        logExPrev = logExPrev + ')';
                    }
                }

                if (logEx == '' || logEx == ')') return;

                this.element.setAttribute('data-talelogic', logEx);

                var ifCondition = this.element.findOne('.talelogic-if-condition');
                ifCondition.setText('if ' + logExPrev + ':');
            }
        } );
        editor.widgets.add( 'TaleLogicInline', {
            button: 'Add Conditional Inline Text',

            dialog: 'talelogicinlineDialog',

            template: '<span class="talelogic-outer" data-talelogic="LOGIC_GOES_HERE">' +
                '<span class="talelogic-if"><span class="talelogic-if-condition">LOGIC GOES HERE...</span><span class="talelogic-if-text"><span></span></span></span>' +
                '<span class="talelogic-else"><span class="talelogic-else-condition">else:</span><span class="talelogic-else-text"><span></span></span></span>',

            editables: {
                ifText: {
                    selector: '.talelogic-if-text'
                },
                elseText: {
                    selector: '.talelogic-else-text'
                }
            },

            allowedContent: 'span(!talelogic-outer)[!data-talelogic]; span(!talelogic-if); span(!talelogic-else); span(!talelogic-if-condition); ' +
                'span(!talelogic-if-text); span(!talelogic-else-condition); span(!talelogic-else-text)',

            requiredContent: 'span(talelogic-outer)',

            upcast: function( element ) {
                return element.name == 'span' && element.hasClass( 'talelogic-outer' );
            },

            data: function() {
                var logEx = '';
                var logExPrev = '';

                for (var i = 1; i < 4; i++)
                {
                    for (var j = 1; j < 4; j++)
                    {
                        var tVar = this.data['var_' + i + '_' + j];
                        if (tVar == '-1' || isNaN(tVar)) break;
                        var tVarDesc = this.data['varDesc_' + i + '_' + j];

                        var tCon = this.data['logic_' + i + '_' + j];
                        if (tCon == '-1') break;

                        var tVal = this.data['value_' + i + '_' + j];
                        if (!tVal || tVal == '' || isNaN(tVal)) break;

                        if (j == 1) {
                            if (i != 1) {
                                logEx = logEx + ' or ';
                                logExPrev = logExPrev + ' or ';
                            }
                            logEx = logEx + '(';
                            logExPrev = logExPrev + '(';
                        }

                        if (j != 1) {
                            logEx = logEx + ' and ';
                            logExPrev = logExPrev + ' and ';
                        }
                        logEx = logEx + "{'" + tVar + "'" + ' ' + tCon + ' ' + tVal + "}";
                        logExPrev = logExPrev + '"' + tVarDesc + '"' + ' ' + tCon + ' ' + tVal;
                    }
                    if (logEx.substr(logEx.length - 1) != ')') {
                        logEx = logEx + ')';
                        logExPrev = logExPrev + ')';
                    }
                }

                if (logEx == '' || logEx == ')') return;

                this.element.setAttribute('data-talelogic', logEx);

                var ifCondition = this.element.findOne('.talelogic-if-condition');
                ifCondition.setText('if ' + logExPrev + ':');
            }
        } );
        editor.widgets.add( 'TaleLogicVariable', {
            button: 'Show Variable Value',

            dialog: 'talelogicvariableDialog',

            template: '<span class="talelogic-variable-value" data-talelogic-variable="VARIABLE_ID_HERE">&lt;VARIABLE VALUE WILL SHOW HERE&gt;</span>',

            editables: {
            },

            allowedContent: 'span(!talelogic-variable-value)[!data-talelogic-variable]',

            requiredContent: 'span(talelogic-variable-value)',

            upcast: function( element ) {
                return element.name == 'span' && element.hasClass( 'talelogic-variable-value' );
            },

            data: function() {
                if (this.data['variableId'] == null || this.data['variableId'] == "" || this.data['variableId'] == "-1") {
                    return;
                }
                this.element.setAttribute('data-talelogic-variable', this.data['variableId']);
                this.element.setText('<SHOW "' + this.data['variableName'] + '" VALUE>');
            }
        } );
    }
});