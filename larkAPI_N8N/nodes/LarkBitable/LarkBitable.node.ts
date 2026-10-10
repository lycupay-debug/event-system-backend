import {
  createBitableMethods,
  createLarkClient,
  type BitableMethods,
} from "@lycupay-debug/lark-api";
import {
  NodeConnectionTypes,
  type IExecuteFunctions,
  type INodeExecutionData,
  type INodeType,
  type INodeTypeDescription,
} from "n8n-workflow";

type ResourceName =
  | "apps"
  | "tables"
  | "records"
  | "fields"
  | "views"
  | "forms"
  | "fieldGroups"
  | "dashboards"
  | "roles"
  | "workflows"
  | "blockWorkflows";

const RESOURCE_OPERATIONS: Record<ResourceName, Array<{ name: string; value: string; description: string }>> = {
  apps: [
    { name: "Create", value: "create", description: "Create a Base" },
    { name: "Get", value: "get", description: "Get a Base" },
    { name: "Update", value: "update", description: "Update a Base" },
    { name: "Copy", value: "copy", description: "Copy a Base" },
  ],
  tables: [
    { name: "Create", value: "create", description: "Create a table" },
    { name: "List", value: "list", description: "List tables" },
    { name: "Update", value: "update", description: "Update a table" },
    { name: "Delete", value: "delete", description: "Delete a table" },
    { name: "Batch Create", value: "batchCreate", description: "Create multiple tables" },
    { name: "Batch Delete", value: "batchDelete", description: "Delete multiple tables" },
  ],
  records: [
    { name: "Create", value: "create", description: "Create a record" },
    { name: "Get", value: "get", description: "Get a record" },
    { name: "List", value: "list", description: "List records" },
    { name: "Search", value: "search", description: "Search records" },
    { name: "Update", value: "update", description: "Update a record" },
    { name: "Delete", value: "delete", description: "Delete a record" },
    { name: "Batch Create", value: "batchCreate", description: "Create multiple records" },
    { name: "Batch Get", value: "batchGet", description: "Get multiple records" },
    { name: "Batch Update", value: "batchUpdate", description: "Update multiple records" },
    { name: "Batch Delete", value: "batchDelete", description: "Delete multiple records" },
  ],
  fields: [
    { name: "Create", value: "create", description: "Create a field" },
    { name: "List", value: "list", description: "List fields" },
    { name: "Update", value: "update", description: "Update a field" },
    { name: "Delete", value: "delete", description: "Delete a field" },
  ],
  views: [
    { name: "Create", value: "create", description: "Create a view" },
    { name: "Get", value: "get", description: "Get a view" },
    { name: "List", value: "list", description: "List views" },
    { name: "Update", value: "update", description: "Update a view" },
    { name: "Delete", value: "delete", description: "Delete a view" },
  ],
  forms: [
    { name: "Get", value: "get", description: "Get form settings" },
    { name: "Update", value: "update", description: "Update form settings" },
    { name: "Upgrade", value: "upgrade", description: "Upgrade a form" },
    { name: "List Fields", value: "listFields", description: "List form fields" },
    { name: "Update Field", value: "updateField", description: "Update a form field" },
  ],
  fieldGroups: [
    { name: "Create", value: "create", description: "Create a field group" },
  ],
  dashboards: [
    { name: "List", value: "list", description: "List dashboards" },
    { name: "Copy", value: "copy", description: "Copy a dashboard" },
  ],
  roles: [
    { name: "Create", value: "create", description: "Create a custom role" },
    { name: "List", value: "list", description: "List custom roles" },
    { name: "Update", value: "update", description: "Update a custom role" },
    { name: "Delete", value: "delete", description: "Delete a custom role" },
    { name: "List Members", value: "listMembers", description: "List role members" },
    { name: "Create Member", value: "createMember", description: "Add a role member" },
    { name: "Batch Create Members", value: "batchCreateMembers", description: "Add multiple role members" },
    { name: "Delete Member", value: "deleteMember", description: "Remove a role member" },
    { name: "Batch Delete Members", value: "batchDeleteMembers", description: "Remove multiple role members" },
  ],
  workflows: [
    { name: "List", value: "list", description: "List Bitable workflows" },
    { name: "Update", value: "update", description: "Update a Bitable workflow" },
  ],
  blockWorkflows: [
    { name: "List", value: "list", description: "List block workflows" },
  ],
};

const RESOURCE_NAMES: Array<{ name: string; value: ResourceName }> = [
  { name: "Base", value: "apps" },
  { name: "Table", value: "tables" },
  { name: "Record", value: "records" },
  { name: "Field", value: "fields" },
  { name: "View", value: "views" },
  { name: "Form", value: "forms" },
  { name: "Field Group", value: "fieldGroups" },
  { name: "Dashboard", value: "dashboards" },
  { name: "Custom Role", value: "roles" },
  { name: "Workflow", value: "workflows" },
  { name: "Block Workflow", value: "blockWorkflows" },
];

function parsePayload(value: unknown): Record<string, unknown> {
  if (typeof value === "string") {
    try {
      const parsed: unknown = JSON.parse(value);
      if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
        throw new Error("Payload JSON must be an object.");
      }
      return parsed as Record<string, unknown>;
    } catch (error) {
      if (error instanceof Error && error.message === "Payload JSON must be an object.") {
        throw error;
      }
      throw new Error("Payload must be valid JSON containing an object.");
    }
  }
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("Payload must be a JSON object.");
  }
  return value as Record<string, unknown>;
}

function toOutputJson(value: unknown): INodeExecutionData["json"] {
  if (value === undefined) return {};
  if (value === null) return { result: null };
  if (typeof value === "object" && !Array.isArray(value)) {
    return value as INodeExecutionData["json"];
  }
  return { result: value as string | number | boolean | object };
}

export class LarkBitable implements INodeType {
  description: INodeTypeDescription = {
    displayName: "Feishu/Lark Bitable",
    name: "larkBitable",
    icon: "file:larkBitable.svg",
    group: ["input"],
    version: 1,
    subtitle: '={{$parameter["resource"] + ": " + $parameter["operation"]}}',
    description: "Use the typed API method library to access Feishu/Lark Bitable.",
    defaults: { name: "Feishu/Lark Bitable" },
    inputs: [NodeConnectionTypes.Main],
    outputs: [NodeConnectionTypes.Main],
    credentials: [{ name: "larkBitableApi", required: true }],
    properties: [
      {
        displayName: "Resource",
        name: "resource",
        type: "options",
        noDataExpression: true,
        options: RESOURCE_NAMES.map((item) => ({ name: item.name, value: item.value })),
        default: "records",
      },
      ...RESOURCE_NAMES.map((resource) => ({
        displayName: "Operation",
        name: "operation",
        type: "options" as const,
        noDataExpression: true,
        displayOptions: { show: { resource: [resource.value] } },
        options: RESOURCE_OPERATIONS[resource.value].map((operation) => ({
          name: operation.name,
          value: operation.value,
          description: operation.description,
          action: operation.description,
        })),
        default: RESOURCE_OPERATIONS[resource.value][0].value,
      })),
      {
        displayName: "Payload",
        name: "payload",
        type: "json",
        default: "{}",
        required: true,
        description: "Complete request object expected by the official SDK method. Include path, query, and data keys as required by that endpoint.",
      },
      {
        displayName: "Note",
        name: "usageNote",
        type: "notice",
        default: "",
        displayOptions: { show: { resource: ["records"] } },
        description: "For example, a list-records request typically supplies path.app_token, path.table_id, and query.page_size/page_token. Check the official API reference for the selected operation's required fields.",
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const credentials = await this.getCredentials("larkBitableApi");
    const client = createLarkClient({
      appId: String(credentials.appId ?? ""),
      appSecret: String(credentials.appSecret ?? ""),
      platform: credentials.platform === "lark" ? "lark" : "feishu",
    });
    const bitable: BitableMethods = createBitableMethods(client);
    const inputItems = this.getInputData();
    const output: INodeExecutionData[] = [];

    for (let i = 0; i < inputItems.length; i++) {
      try {
        const resource = this.getNodeParameter("resource", i) as ResourceName;
        const operation = this.getNodeParameter("operation", i) as string;
        const payload = parsePayload(this.getNodeParameter("payload", i));
        const resourceMethods = bitable[resource] as unknown as Record<string, (arg: Record<string, unknown>) => Promise<unknown>>;
        const method = resourceMethods?.[operation];
        if (typeof method !== "function") {
          throw new Error(`Unsupported Bitable operation: ${resource}.${operation}`);
        }

        const result = await method(payload);
        output.push({
          json: toOutputJson(result),
          pairedItem: { item: i },
        });
      } catch (error) {
        if (this.continueOnFail()) {
          output.push({
            json: { error: error instanceof Error ? error.message : String(error) },
            pairedItem: { item: i },
          });
          continue;
        }
        if (error instanceof Error) {
          throw error;
        }
        throw new Error(String(error));
      }
    }

    return [output];
  }
}
