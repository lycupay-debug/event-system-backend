import type {
  ICredentialType,
  INodeProperties,
} from "n8n-workflow";

export class LarkBitableApi implements ICredentialType {
  name = "larkBitableApi";
  displayName = "Feishu/Lark Bitable API";
  documentationUrl = "https://open.larksuite.com/document/";
  properties: INodeProperties[] = [
    {
      displayName: "Platform",
      name: "platform",
      type: "options",
      options: [
        { name: "Feishu (China)", value: "feishu" },
        { name: "Lark (International)", value: "lark" },
      ],
      default: "feishu",
      description: "Select the Open Platform domain for your tenant.",
    },
    {
      displayName: "App ID",
      name: "appId",
      type: "string",
      default: "",
      required: true,
    },
    {
      displayName: "App Secret",
      name: "appSecret",
      type: "string",
      typeOptions: { password: true },
      default: "",
      required: true,
    },
  ];
}
