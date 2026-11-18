module.exports = {
 id: "EVENT_DEAD_DROP", name: "Dead Drop: Runtime command", groups: ["EVENT_GROUP_MISC"],
 fields: [{key:"op",label:"Command (0 reset, 1 sector, 2 supply, 3 blackout, 4 hide HUD)",type:"number",defaultValue:1},{key:"value",label:"Value",type:"number",defaultValue:0}],
 compile: (input,helpers) => {
  helpers._stackPushConst(input.op || 0);
  helpers._stackPushConst(input.value || 0);
  helpers._callNative("dd_command");
  helpers._stackPop(2);
 }
};
