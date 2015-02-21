/**
 * Created by brkrs_000 on 20.2.2015.
 */
CKEDITOR.plugins.add( 'talelogic', {
    requires: 'widget',
    icons: 'talelogic',
    init: function( editor ) {
        CKEDITOR.dialog.add( 'talelogicDialog', this.path + 'dialogs/talelogic.js' );
        editor.widgets.add( 'TaleLogic', {
            button: 'Add Conditional Text',

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
    }
});